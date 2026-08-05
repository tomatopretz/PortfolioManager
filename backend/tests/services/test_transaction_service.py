import os
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.PortfolioItemDTO import PortfolioItemDTO
from models.RecordTransactionRequestDTO import CASH_ASSET_TYPE, CASH_TICKER, RecordTransactionRequestDTO
from models.TransactionDTO import TransactionDTO
from services.transaction_service import InsufficientBalanceError, PortfolioItemNotFoundError, TransactionService


def _item(ticker, quantity, cost_basis, asset_type='stock'):
    return PortfolioItemDTO(
        id=str(uuid.uuid4()), ticker=ticker, assetType=asset_type, quantity=quantity, costBasis=cost_basis,
        lastUpdated=datetime.now(timezone.utc),
    )


def _cash_item(quantity=1000, cost_basis=1000):
    return PortfolioItemDTO(
        id=str(uuid.uuid4()), ticker=CASH_TICKER, assetType=CASH_ASSET_TYPE, quantity=quantity, costBasis=cost_basis,
        lastUpdated=datetime.now(timezone.utc),
    )


def _request(**overrides):
    defaults = dict(type='buy', ticker='AAPL', assetType='STOCK', quantity=10, price=100, useCash=True)
    defaults.update(overrides)
    return RecordTransactionRequestDTO(**defaults)


def _lookup_by_asset_type(cash_item=None, stock_item=None):
    """Build a side_effect for get_by_ticker_and_asset_type that returns cash_item when asked
    for CASH, and stock_item for anything else - regardless of call order."""
    def _lookup(ticker, asset_type, conn=None, for_update=False):
        return cash_item if asset_type == CASH_ASSET_TYPE else stock_item
    return _lookup


def _txn(portfolio_item_id, type_, quantity, date=None, price=1, useCash=False):
    return TransactionDTO(
        id=str(uuid.uuid4()), portfolioItemId=portfolio_item_id, type=type_, quantity=quantity,
        price=price, date=date or datetime(2020, 1, 1, tzinfo=timezone.utc), useCash=useCash,
    )


def _seed_history(*items):
    """Build side_effects for (get_latest_date, list_by_portfolio_item), seeding each item's
    history with a single old 'buy' transaction reconstructing its current .quantity. Covers
    both of `_validate_debit`'s paths consistently - the fast path only needs get_latest_date,
    the slow path needs list_by_portfolio_item too - for tests that aren't specifically
    exercising the backdated/replay behavior itself."""
    history = {item.id: [_txn(item.id, 'buy', item.quantity)] for item in items}

    def _latest_date(portfolio_item_id, conn=None):
        txns = history.get(portfolio_item_id, [])
        return max((t.date for t in txns), default=None)

    def _list(portfolio_item_id, conn=None):
        return history.get(portfolio_item_id, [])

    return _latest_date, _list


def _fake_repo_add(entity, conn=None):
    """Mimic PortfolioItemRepository.add/TransactionRepository.add: mutate .id in place and
    return the same object, like the real repo methods do."""
    entity.id = entity.id or str(uuid.uuid4())
    return entity


@contextmanager
def _fake_transaction():
    yield MagicMock()


@pytest.fixture(autouse=True)
def _mock_get_transaction():
    # mock: applied to every test in this file - replaces the real DB transaction context manager
    # with a fake one, so record_transaction() never touches an actual connection
    with patch('services.transaction_service.get_transaction', side_effect=_fake_transaction):
        yield


# --- list_transactions --------------------------------------------------------------------

@patch('services.transaction_service.TransactionRepository.list_all')  # mock: replace the repository so no real DB call runs
def test_list_transactions_returns_all_when_no_tickers_given(mock_list_all):
    # Given the repository returns one transaction
    mock_list_all.return_value = ['txn']
    # When/Then listing with no ticker filter delegates to list_all()
    assert TransactionService.list_transactions() == ['txn']
    mock_list_all.assert_called_once()


@patch('services.transaction_service.TransactionRepository.list_by_tickers')  # mock: replace the repository so no real DB call runs
def test_list_transactions_filters_by_tickers(mock_list_by_tickers):
    # Given the repository returns one transaction
    mock_list_by_tickers.return_value = ['txn']
    # When/Then listing with a ticker filter delegates to list_by_tickers()
    assert TransactionService.list_transactions(['AAPL']) == ['txn']
    mock_list_by_tickers.assert_called_once_with(['AAPL'])


# --- export_transactions_csv ------------------------------------------------------------------

@patch('services.transaction_service.TransactionRepository.list_export_rows')  # mock: no DB call
def test_export_transactions_csv_includes_cash_and_use_cash(mock_export_rows):
    # Given export rows already include ticker/type from the backend join
    mock_export_rows.return_value = [
        {
            'date': datetime(2026, 1, 1, tzinfo=timezone.utc),
            'ticker': 'USD',
            'assetType': 'CASH',
            'type': 'buy',
            'quantity': 1000,
            'price': 1,
            'useCash': False,
        },
        {
            'date': datetime(2026, 1, 2, tzinfo=timezone.utc),
            'ticker': 'TLT',
            'assetType': 'BOND',
            'type': 'buy',
            'quantity': 10,
            'price': 90,
            'useCash': True,
        },
    ]

    # When exporting CSV
    result = TransactionService.export_transactions_csv()

    # Then it uses the import-compatible schema, including cash actions and UseCash
    assert result == (
        'Date,Ticker,Type,Action,Quantity,Price,UseCash\n'
        '2026-01-01,USD,CASH,DEPOSIT,1000,1,FALSE\n'
        '2026-01-02,TLT,BOND,BUY,10,90,TRUE\n'
    )


# --- record_transactions_bulk ----------------------------------------------------------------

@patch('services.transaction_service._remove_asset')  # mock: skip real sell/cash/portfolio writes
@patch('services.transaction_service._add_asset')  # mock: skip real buy/cash/portfolio writes
@patch('services.transaction_service.get_transaction')  # mock: replace the DB transaction context
def test_record_transactions_bulk_uses_one_transaction_context(mock_get_transaction, mock_add_asset, mock_remove_asset):
    # Given two requests and one fake DB transaction context
    conn = MagicMock()

    @contextmanager
    def _tracked_transaction():
        yield conn

    buy_request = _request(type='buy', date=datetime(2026, 1, 1, tzinfo=timezone.utc))
    sell_request = _request(type='sell', date=datetime(2026, 1, 2, tzinfo=timezone.utc))
    buy_txn = _txn(str(uuid.uuid4()), 'buy', 10, buy_request.date)
    sell_txn = _txn(str(uuid.uuid4()), 'sell', 10, sell_request.date)
    mock_get_transaction.side_effect = _tracked_transaction
    mock_add_asset.return_value = buy_txn
    mock_remove_asset.return_value = sell_txn

    # When recording both in bulk
    result = TransactionService.record_transactions_bulk([buy_request, sell_request])

    # Then one DB transaction spans both rows, while the same buy/sell helpers do the real work
    assert result == [buy_txn, sell_txn]
    mock_get_transaction.assert_called_once_with()
    mock_add_asset.assert_called_once_with(buy_request, buy_request.date, conn)
    mock_remove_asset.assert_called_once_with(sell_request, sell_request.date, conn)


@patch('services.transaction_service._remove_asset')  # mock: skip real sell/cash/portfolio writes
@patch('services.transaction_service._add_asset')  # mock: skip real buy/cash/portfolio writes
@patch('services.transaction_service.get_transaction')  # mock: replace the DB transaction context
def test_record_transactions_bulk_processes_requests_by_date(mock_get_transaction, mock_add_asset, mock_remove_asset):
    # Given the CSV/import order puts a sell before its earlier buy
    conn = MagicMock()

    @contextmanager
    def _tracked_transaction():
        yield conn

    sell_request = _request(type='sell', date=datetime(2026, 2, 1, tzinfo=timezone.utc))
    buy_request = _request(type='buy', date=datetime(2026, 1, 1, tzinfo=timezone.utc))
    mock_get_transaction.side_effect = _tracked_transaction
    mock_add_asset.return_value = _txn(str(uuid.uuid4()), 'buy', 10, buy_request.date)
    mock_remove_asset.return_value = _txn(str(uuid.uuid4()), 'sell', 10, sell_request.date)

    # When recording in bulk
    TransactionService.record_transactions_bulk([sell_request, buy_request])

    # Then the earlier buy is applied first, so sells can find the holding they depend on
    calls = mock_add_asset.mock_calls + mock_remove_asset.mock_calls
    assert calls[0].args == (buy_request, buy_request.date, conn)
    assert calls[1].args == (sell_request, sell_request.date, conn)


@patch('services.transaction_service._remove_asset')  # mock: force a row failure
@patch('services.transaction_service._add_asset')  # mock: skip real first-row write
@patch('services.transaction_service.get_transaction')  # mock: replace the DB transaction context
def test_record_transactions_bulk_propagates_row_failure(mock_get_transaction, mock_add_asset, mock_remove_asset):
    # Given the second row fails while both rows are inside the same transaction context
    conn = MagicMock()

    @contextmanager
    def _tracked_transaction():
        yield conn

    mock_get_transaction.side_effect = _tracked_transaction
    mock_add_asset.return_value = _txn(str(uuid.uuid4()), 'buy', 10)
    mock_remove_asset.side_effect = InsufficientBalanceError("'AAPL' quantity 5 is less than the 10 required")

    # When/Then the bulk call raises so psycopg's transaction context can roll the batch back
    with pytest.raises(InsufficientBalanceError):
        TransactionService.record_transactions_bulk([_request(type='buy'), _request(type='sell')])

    mock_get_transaction.assert_called_once_with()


# --- record_transaction: date handling ---------------------------------------------------------

@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)  # mock: fake insert, no real DB call
@patch('services.transaction_service.TransactionRepository.list_by_portfolio_item')  # mock: no real DB call
@patch('services.transaction_service.TransactionRepository.get_latest_date')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.update')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_record_transaction_uses_client_supplied_date_when_given(
    mock_get_item, mock_update_item, mock_latest_date, mock_list_history, mock_add_txn,
):
    # Given an existing CASH item and a client-supplied backdated date
    cash = _cash_item(quantity=1000, cost_basis=1000)
    mock_get_item.return_value = cash
    mock_latest_date.side_effect, mock_list_history.side_effect = _seed_history(cash)
    backdated = datetime(2026, 1, 1, tzinfo=timezone.utc)

    # When recording a withdrawal with that date
    request = _request(type='sell', ticker='usd', assetType='cash', quantity=100, price=None, date=backdated)
    result = TransactionService.record_transaction(request)

    # Then the recorded transaction keeps the client-supplied date, not now()
    assert result.date == backdated


@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)  # mock: fake insert, no real DB call
@patch('services.transaction_service.TransactionRepository.list_by_portfolio_item')  # mock: no real DB call
@patch('services.transaction_service.TransactionRepository.get_latest_date')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.update')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_record_transaction_defaults_date_to_now_when_omitted(
    mock_get_item, mock_update_item, mock_latest_date, mock_list_history, mock_add_txn,
):
    # Given an existing CASH item and no date on the request
    cash = _cash_item(quantity=1000, cost_basis=1000)
    mock_get_item.return_value = cash
    mock_latest_date.side_effect, mock_list_history.side_effect = _seed_history(cash)
    before = datetime.now(timezone.utc)

    # When recording a withdrawal with no date
    request = _request(type='sell', ticker='usd', assetType='cash', quantity=100, price=None)
    result = TransactionService.record_transaction(request)

    # Then the recorded transaction's date defaults to "now", bounded by before/after this call
    after = datetime.now(timezone.utc)
    assert before <= result.date <= after


# --- record_transaction: ADD flow (type='buy') ----------------------------------------------

@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)  # mock: fake insert, no real DB call
@patch('services.transaction_service.PortfolioItemRepository.update')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.add', side_effect=_fake_repo_add)  # mock: fake insert, no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_deposit_cash_creates_cash_item_on_first_deposit(mock_get_item, mock_add_item, mock_update_item, mock_add_txn):
    # Given no CASH item exists yet
    mock_get_item.return_value = None  # no CASH item exists yet

    # When depositing cash for the first time
    request = _request(type='buy', ticker='usd', assetType='cash', quantity=500, price=None, useCash=False)
    result = TransactionService.record_transaction(request)

    # Then a new CASH item is created and immediately updated with the deposited balance
    added_item = mock_add_item.call_args[0][0]
    assert added_item.ticker == CASH_TICKER
    assert added_item.assetType == CASH_ASSET_TYPE

    updated_item = mock_update_item.call_args[0][0]
    assert updated_item.quantity == 500
    assert updated_item.costBasis == 500  # cash costBasis mirrors quantity 1:1

    # And the recorded transaction reflects a direct deposit (useCash=False)
    assert result.type == 'buy'
    assert result.quantity == 500
    assert result.price == 1
    assert result.useCash is False


@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)  # mock: fake insert, no real DB call
@patch('services.transaction_service.PortfolioItemRepository.update')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_deposit_cash_updates_existing_cash_item(mock_get_item, mock_update_item, mock_add_txn):
    # Given an existing CASH item with a balance
    existing_cash = _cash_item(quantity=1000, cost_basis=1000)
    mock_get_item.return_value = existing_cash

    # When depositing more cash
    request = _request(type='buy', ticker='usd', assetType='cash', quantity=250, price=None, useCash=False)
    result = TransactionService.record_transaction(request)

    # Then the existing item's balance is incremented, not replaced
    updated_item = mock_update_item.call_args[0][0]
    assert updated_item.quantity == 1250
    assert updated_item.costBasis == 1250

    assert result.quantity == 250
    assert result.price == 1
    assert result.portfolioItemId == existing_cash.id


@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)  # mock: fake insert, no real DB call
@patch('services.transaction_service.PortfolioItemRepository.update')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.add', side_effect=_fake_repo_add)  # mock: fake insert, no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_buy_asset_without_cash_creates_new_item_and_skips_cash_check(
    mock_get_item, mock_add_item, mock_update_item, mock_add_txn,
):
    # Given the stock doesn't exist in the portfolio yet
    mock_get_item.return_value = None  # AAPL doesn't exist yet

    # When buying it with useCash=False (funded externally, not from the CASH balance)
    request = _request(type='buy', ticker='aapl', assetType='stock', quantity=10, price=150, useCash=False)
    result = TransactionService.record_transaction(request)

    # Then the CASH balance is never even looked up, and a new stock item is created
    assert mock_get_item.call_count == 1  # only the stock lookup - cash is never checked
    assert mock_get_item.call_args[0] == ('AAPL', 'STOCK')

    added_item = mock_add_item.call_args[0][0]
    assert added_item.ticker == 'AAPL'
    assert added_item.assetType == 'STOCK'

    mock_update_item.assert_not_called()  # nothing pre-existing to update
    assert result.type == 'buy'
    assert result.price == 150
    assert result.useCash is False


@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)  # mock: fake insert, no real DB call
@patch('services.transaction_service.PortfolioItemRepository.update')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_buy_asset_existing_item_accumulates_quantity_and_cost_basis(mock_get_item, mock_update_item, mock_add_txn):
    # Given an existing AAPL holding
    mock_get_item.return_value = _item('AAPL', quantity=5, cost_basis=500, asset_type='STOCK')

    # When buying more of it
    request = _request(type='buy', ticker='aapl', assetType='stock', quantity=5, price=120, useCash=False)
    TransactionService.record_transaction(request)

    # Then quantity and cost basis both accumulate onto the existing item
    updated_item = mock_update_item.call_args[0][0]
    assert updated_item.quantity == 10
    assert updated_item.costBasis == 500 + 600  # existing 500 + (5 * 120)


@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)  # mock: fake insert, no real DB call
@patch('services.transaction_service.TransactionRepository.list_by_portfolio_item')  # mock: no real DB call
@patch('services.transaction_service.TransactionRepository.get_latest_date')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.update')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_buy_asset_with_cash_deducts_balance_and_records_both_transactions(
    mock_get_item, mock_update_item, mock_latest_date, mock_list_history, mock_add_txn,
):
    # Given a CASH balance and an existing AAPL holding
    cash = _cash_item(quantity=2000, cost_basis=2000)
    stock = _item('AAPL', quantity=5, cost_basis=500, asset_type='STOCK')
    mock_get_item.side_effect = _lookup_by_asset_type(cash_item=cash, stock_item=stock)
    mock_latest_date.side_effect, mock_list_history.side_effect = _seed_history(cash)

    # When buying more AAPL funded from the CASH balance (useCash=True)
    request = _request(type='buy', ticker='aapl', assetType='stock', quantity=10, price=150, useCash=True)
    result = TransactionService.record_transaction(request)

    # Then both the CASH balance (deducted) and the stock item (accumulated) are updated
    assert mock_update_item.call_count == 2  # cash deduction + stock accumulation
    updated_cash, updated_stock = (call[0][0] for call in mock_update_item.call_args_list)
    assert updated_cash.quantity == 2000 - 1500  # 10 * 150
    assert updated_cash.costBasis == 2000 - 1500
    assert updated_stock.quantity == 5 + 10
    assert updated_stock.costBasis == 500 + 1500

    # And two transactions are recorded: the cash-side debit (useCash=True - caused by this
    # trade) plus the stock buy itself
    assert mock_add_txn.call_count == 2  # cash-side debit + the stock buy itself
    cash_txn, stock_txn = (call[0][0] for call in mock_add_txn.call_args_list)
    assert cash_txn.type == 'sell'
    assert cash_txn.quantity == 1500
    assert cash_txn.price == 1
    assert cash_txn.useCash is True

    assert stock_txn.type == 'buy'
    assert stock_txn.quantity == 10
    assert stock_txn.price == 150
    assert stock_txn.useCash is True
    assert result is stock_txn  # record_transaction returns the primary (stock) transaction


@patch('services.transaction_service.TransactionRepository.list_by_portfolio_item')  # mock: no real DB call
@patch('services.transaction_service.TransactionRepository.get_latest_date')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.update')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_buy_asset_with_insufficient_cash_raises(mock_get_item, mock_update_item, mock_latest_date, mock_list_history):
    # Given a CASH balance too small to cover the purchase
    cash = _cash_item(quantity=100, cost_basis=100)  # not enough for 10*150
    mock_get_item.return_value = cash
    mock_latest_date.side_effect, mock_list_history.side_effect = _seed_history(cash)

    # When/Then buying with useCash=True raises before touching any row
    request = _request(type='buy', ticker='aapl', assetType='stock', quantity=10, price=150, useCash=True)
    with pytest.raises(InsufficientBalanceError):
        TransactionService.record_transaction(request)

    mock_update_item.assert_not_called()  # fails before any mutation happens


# --- record_transaction: REMOVE flow (type='sell') ------------------------------------------

@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)  # mock: fake insert, no real DB call
@patch('services.transaction_service.TransactionRepository.list_by_portfolio_item')  # mock: no real DB call
@patch('services.transaction_service.TransactionRepository.get_latest_date')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.update')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_withdraw_cash_success(mock_get_item, mock_update_item, mock_latest_date, mock_list_history, mock_add_txn):
    # Given an existing CASH balance
    cash = _cash_item(quantity=1000, cost_basis=1000)
    mock_get_item.return_value = cash
    mock_latest_date.side_effect, mock_list_history.side_effect = _seed_history(cash)

    # When withdrawing part of it
    request = _request(type='sell', ticker='usd', assetType='cash', quantity=300, price=None)
    result = TransactionService.record_transaction(request)

    # Then the balance is reduced and a matching sell transaction is recorded
    updated_item = mock_update_item.call_args[0][0]
    assert updated_item.quantity == 700
    assert updated_item.costBasis == 700

    assert result.type == 'sell'
    assert result.quantity == 300
    assert result.price == 1


@patch('services.transaction_service.TransactionRepository.list_by_portfolio_item')  # mock: no real DB call
@patch('services.transaction_service.TransactionRepository.get_latest_date')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_withdraw_cash_insufficient_raises(mock_get_item, mock_latest_date, mock_list_history):
    # Given a CASH balance smaller than the requested withdrawal
    cash = _cash_item(quantity=50, cost_basis=50)
    mock_get_item.return_value = cash
    mock_latest_date.side_effect, mock_list_history.side_effect = _seed_history(cash)

    # When/Then withdrawing more than the balance raises
    request = _request(type='sell', ticker='usd', assetType='cash', quantity=100, price=None)
    with pytest.raises(InsufficientBalanceError):
        TransactionService.record_transaction(request)


@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_sell_asset_not_found_raises(mock_get_item):
    # Given the ticker doesn't exist in the portfolio at all
    mock_get_item.return_value = None  # AAPL doesn't exist

    # When/Then selling it raises instead of creating a negative holding
    request = _request(type='sell', ticker='aapl', assetType='stock', quantity=5, price=150)
    with pytest.raises(PortfolioItemNotFoundError):
        TransactionService.record_transaction(request)


@patch('services.transaction_service.TransactionRepository.list_by_portfolio_item')  # mock: no real DB call
@patch('services.transaction_service.TransactionRepository.get_latest_date')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_sell_asset_insufficient_quantity_raises(mock_get_item, mock_latest_date, mock_list_history):
    # Given fewer shares held than requested
    stock = _item('AAPL', quantity=3, cost_basis=300, asset_type='STOCK')
    mock_get_item.return_value = stock
    mock_latest_date.side_effect, mock_list_history.side_effect = _seed_history(stock)

    # When/Then selling more than is held raises
    request = _request(type='sell', ticker='aapl', assetType='stock', quantity=5, price=150)
    with pytest.raises(InsufficientBalanceError):
        TransactionService.record_transaction(request)


@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)  # mock: fake insert, no real DB call
@patch('services.transaction_service.TransactionRepository.list_by_portfolio_item')  # mock: no real DB call
@patch('services.transaction_service.TransactionRepository.get_latest_date')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.update')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_sell_asset_credits_cash_and_reduces_cost_basis_proportionally(
    mock_get_item, mock_update_item, mock_latest_date, mock_list_history, mock_add_txn,
):
    # Given a $100/share average AAPL holding and an existing CASH balance
    stock = _item('AAPL', quantity=10, cost_basis=1000, asset_type='STOCK')  # $100/share average
    cash = _cash_item(quantity=500, cost_basis=500)
    mock_get_item.side_effect = _lookup_by_asset_type(cash_item=cash, stock_item=stock)
    mock_latest_date.side_effect, mock_list_history.side_effect = _seed_history(stock)

    # When selling part of the holding at a different price than the average cost
    request = _request(type='sell', ticker='aapl', assetType='stock', quantity=4, price=120)
    result = TransactionService.record_transaction(request)

    # Then proceeds credit CASH, and the stock's cost basis shrinks proportionally to shares sold
    updated_cash, updated_stock = (call[0][0] for call in mock_update_item.call_args_list)
    assert updated_cash.quantity == 500 + 480  # proceeds = 4 * 120
    assert updated_cash.costBasis == 500 + 480
    assert updated_stock.quantity == 6
    assert updated_stock.costBasis == 600  # $100/share average carried over 6 remaining shares

    # And two transactions are recorded: the cash-side credit (useCash=True - caused by this
    # trade) plus the stock sell itself
    cash_txn, stock_txn = (call[0][0] for call in mock_add_txn.call_args_list)
    assert cash_txn.type == 'buy'
    assert cash_txn.quantity == 480
    assert cash_txn.price == 1
    assert cash_txn.useCash is True

    assert stock_txn.type == 'sell'
    assert stock_txn.quantity == 4
    assert stock_txn.price == 120
    assert stock_txn.useCash is True
    assert result is stock_txn


@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)  # mock: fake insert, no real DB call
@patch('services.transaction_service.TransactionRepository.list_by_portfolio_item')  # mock: no real DB call
@patch('services.transaction_service.TransactionRepository.get_latest_date')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.update')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_sell_asset_to_zero_quantity_keeps_item_instead_of_deleting(
    mock_get_item, mock_update_item, mock_latest_date, mock_list_history, mock_add_txn,
):
    # transaction.portfolio_item_id is ON DELETE CASCADE, so removing the item here would wipe
    # every transaction ever recorded against it - the item must be kept at quantity 0 instead
    # Given a holding of exactly 5 shares
    stock = _item('AAPL', quantity=5, cost_basis=500, asset_type='STOCK')
    cash = _cash_item()
    mock_get_item.side_effect = _lookup_by_asset_type(cash_item=cash, stock_item=stock)
    mock_latest_date.side_effect, mock_list_history.side_effect = _seed_history(stock)

    # When selling all 5 shares
    request = _request(type='sell', ticker='aapl', assetType='stock', quantity=5, price=150)
    TransactionService.record_transaction(request)

    # Then the item is updated to quantity 0 rather than removed
    _, updated_stock = (call[0][0] for call in mock_update_item.call_args_list)
    assert updated_stock.quantity == 0
    assert updated_stock.costBasis == 0


# --- record_transaction: backdated transactions -----------------------------------------------

@patch('services.transaction_service.TransactionRepository.list_by_portfolio_item')  # mock: no real DB call
@patch('services.transaction_service.TransactionRepository.get_latest_date')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_sell_asset_backdated_before_the_buy_that_funded_it_raises(mock_get_item, mock_latest_date, mock_list_history):
    # Given META was bought today - item.quantity (10) already reflects that buy
    stock = _item('META', quantity=10, cost_basis=1000, asset_type='STOCK')
    mock_get_item.return_value = stock
    today_buy = _txn(stock.id, 'buy', 10, date=datetime(2026, 1, 15, tzinfo=timezone.utc))
    mock_latest_date.return_value = today_buy.date  # backdated request is < this, so triggers the slow path
    mock_list_history.return_value = [today_buy]

    # When/Then selling those shares dated *before* the buy raises - at that point in time, on
    # the actual timeline, nothing had been bought yet
    request = _request(
        type='sell', ticker='meta', assetType='stock', quantity=10, price=150,
        date=datetime(2026, 1, 14, tzinfo=timezone.utc),
    )
    with pytest.raises(InsufficientBalanceError):
        TransactionService.record_transaction(request)


@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)  # mock: fake insert, no real DB call
@patch('services.transaction_service.TransactionRepository.list_by_portfolio_item')  # mock: no real DB call
@patch('services.transaction_service.TransactionRepository.get_latest_date')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.update')  # mock: no real DB call
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_sell_asset_backdated_between_two_buys_still_forces_replay_and_succeeds(
    mock_get_item, mock_update_item, mock_latest_date, mock_list_history, mock_add_txn,
):
    # Given META was bought in two batches: 10 shares on day 1, another 5 on day 20 (15 today)
    stock = _item('META', quantity=15, cost_basis=1500, asset_type='STOCK')
    cash = _cash_item()
    mock_get_item.side_effect = _lookup_by_asset_type(cash_item=cash, stock_item=stock)
    first_buy = _txn(stock.id, 'buy', 10, date=datetime(2026, 1, 10, tzinfo=timezone.utc))
    second_buy = _txn(stock.id, 'buy', 5, date=datetime(2026, 1, 20, tzinfo=timezone.utc))
    mock_latest_date.return_value = second_buy.date  # request date below is earlier -> forces the slow path
    mock_list_history.return_value = [first_buy, second_buy]

    # When selling some of it dated day 15 - after the first buy, before the second, so this is
    # a genuinely backdated insertion that only the full replay (not the fast path) can validate
    request = _request(
        type='sell', ticker='meta', assetType='stock', quantity=4, price=150,
        date=datetime(2026, 1, 15, tzinfo=timezone.utc),
    )
    result = TransactionService.record_transaction(request)

    # Then it succeeds: replaying buy10 -> sell4 -> buy5 never goes negative (10, 6, 11)
    assert result.type == 'sell'
    assert result.quantity == 4


@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')  # mock: no real DB call
def test_sell_asset_backdated_insertion_that_invalidates_a_later_sell_raises(mock_get_item):
    # Given a timeline where a sell already relies on an earlier buy to stay non-negative:
    # buy 10 (day 1) -> sell 8 (day 5), leaving 2 - the day-5 sell was valid against a running
    # balance of 10 at the time
    stock = _item('META', quantity=2, cost_basis=200, asset_type='STOCK')
    mock_get_item.return_value = stock
    day1_buy = _txn(stock.id, 'buy', 10, date=datetime(2026, 1, 1, tzinfo=timezone.utc))
    day5_sell = _txn(stock.id, 'sell', 8, date=datetime(2026, 1, 5, tzinfo=timezone.utc))

    with (
        patch('services.transaction_service.TransactionRepository.get_latest_date') as mock_latest_date,
        patch('services.transaction_service.TransactionRepository.list_by_portfolio_item') as mock_list_history,
    ):
        mock_latest_date.return_value = day5_sell.date  # request date below is earlier -> forces the slow path
        mock_list_history.return_value = [day1_buy, day5_sell]

        # When/Then inserting a backdated sell of 5 on day 3 is valid in isolation at that point
        # (10 - 5 = 5 >= 0), but retroactively drives the existing day-5 sell negative
        # (5 - 8 = -3) - so the whole insertion must be rejected, not just checked at day 3
        request = _request(
            type='sell', ticker='meta', assetType='stock', quantity=5, price=150,
            date=datetime(2026, 1, 3, tzinfo=timezone.utc),
        )
        with pytest.raises(InsufficientBalanceError):
            TransactionService.record_transaction(request)
