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
from services.transaction_service import (
    InsufficientCashError,
    InsufficientQuantityError,
    PortfolioItemNotFoundError,
    TransactionService,
)


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
    with patch('services.transaction_service.get_transaction', side_effect=_fake_transaction):
        yield


# --- list_transactions --------------------------------------------------------------------

@patch('services.transaction_service.TransactionRepository.list_all')
def test_list_transactions_returns_all_when_no_tickers_given(mock_list_all):
    mock_list_all.return_value = ['txn']
    assert TransactionService.list_transactions() == ['txn']
    mock_list_all.assert_called_once()


@patch('services.transaction_service.TransactionRepository.list_by_tickers')
def test_list_transactions_filters_by_tickers(mock_list_by_tickers):
    mock_list_by_tickers.return_value = ['txn']
    assert TransactionService.list_transactions(['AAPL']) == ['txn']
    mock_list_by_tickers.assert_called_once_with(['AAPL'])


# --- record_transaction: date handling ---------------------------------------------------------

@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)
@patch('services.transaction_service.PortfolioItemRepository.update')
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')
def test_record_transaction_uses_client_supplied_date_when_given(mock_get_item, mock_update_item, mock_add_txn):
    mock_get_item.return_value = _cash_item(quantity=1000, cost_basis=1000)
    backdated = datetime(2026, 1, 1, tzinfo=timezone.utc)

    request = _request(type='sell', ticker='usd', assetType='cash', quantity=100, price=None, date=backdated)
    result = TransactionService.record_transaction(request)

    assert result.date == backdated


@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)
@patch('services.transaction_service.PortfolioItemRepository.update')
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')
def test_record_transaction_defaults_date_to_now_when_omitted(mock_get_item, mock_update_item, mock_add_txn):
    mock_get_item.return_value = _cash_item(quantity=1000, cost_basis=1000)
    before = datetime.now(timezone.utc)

    request = _request(type='sell', ticker='usd', assetType='cash', quantity=100, price=None)
    result = TransactionService.record_transaction(request)

    after = datetime.now(timezone.utc)
    assert before <= result.date <= after


# --- record_transaction: ADD flow (type='buy') ----------------------------------------------

@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)
@patch('services.transaction_service.PortfolioItemRepository.update')
@patch('services.transaction_service.PortfolioItemRepository.add', side_effect=_fake_repo_add)
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')
def test_deposit_cash_creates_cash_item_on_first_deposit(mock_get_item, mock_add_item, mock_update_item, mock_add_txn):
    mock_get_item.return_value = None  # no CASH item exists yet

    request = _request(type='buy', ticker='usd', assetType='cash', quantity=500, price=None, useCash=False)
    result = TransactionService.record_transaction(request)

    added_item = mock_add_item.call_args[0][0]
    assert added_item.ticker == CASH_TICKER
    assert added_item.assetType == CASH_ASSET_TYPE

    updated_item = mock_update_item.call_args[0][0]
    assert updated_item.quantity == 500
    assert updated_item.costBasis == 500  # cash costBasis mirrors quantity 1:1

    assert result.type == 'buy'
    assert result.quantity == 500
    assert result.price == 1
    assert result.useCash is False


@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)
@patch('services.transaction_service.PortfolioItemRepository.update')
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')
def test_deposit_cash_updates_existing_cash_item(mock_get_item, mock_update_item, mock_add_txn):
    existing_cash = _cash_item(quantity=1000, cost_basis=1000)
    mock_get_item.return_value = existing_cash

    request = _request(type='buy', ticker='usd', assetType='cash', quantity=250, price=None, useCash=False)
    result = TransactionService.record_transaction(request)

    updated_item = mock_update_item.call_args[0][0]
    assert updated_item.quantity == 1250
    assert updated_item.costBasis == 1250

    assert result.quantity == 250
    assert result.price == 1
    assert result.portfolioItemId == existing_cash.id


@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)
@patch('services.transaction_service.PortfolioItemRepository.update')
@patch('services.transaction_service.PortfolioItemRepository.add', side_effect=_fake_repo_add)
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')
def test_buy_asset_without_cash_creates_new_item_and_skips_cash_check(
    mock_get_item, mock_add_item, mock_update_item, mock_add_txn,
):
    mock_get_item.return_value = None  # AAPL doesn't exist yet

    request = _request(type='buy', ticker='aapl', assetType='stock', quantity=10, price=150, useCash=False)
    result = TransactionService.record_transaction(request)

    assert mock_get_item.call_count == 1  # only the stock lookup - cash is never checked
    assert mock_get_item.call_args[0] == ('AAPL', 'STOCK')

    added_item = mock_add_item.call_args[0][0]
    assert added_item.ticker == 'AAPL'
    assert added_item.assetType == 'STOCK'

    mock_update_item.assert_not_called()  # nothing pre-existing to update
    assert result.type == 'buy'
    assert result.price == 150
    assert result.useCash is False


@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)
@patch('services.transaction_service.PortfolioItemRepository.update')
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')
def test_buy_asset_existing_item_accumulates_quantity_and_cost_basis(mock_get_item, mock_update_item, mock_add_txn):
    mock_get_item.return_value = _item('AAPL', quantity=5, cost_basis=500, asset_type='STOCK')

    request = _request(type='buy', ticker='aapl', assetType='stock', quantity=5, price=120, useCash=False)
    TransactionService.record_transaction(request)

    updated_item = mock_update_item.call_args[0][0]
    assert updated_item.quantity == 10
    assert updated_item.costBasis == 500 + 600  # existing 500 + (5 * 120)


@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)
@patch('services.transaction_service.PortfolioItemRepository.update')
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')
def test_buy_asset_with_cash_deducts_balance_and_records_both_transactions(mock_get_item, mock_update_item, mock_add_txn):
    cash = _cash_item(quantity=2000, cost_basis=2000)
    stock = _item('AAPL', quantity=5, cost_basis=500, asset_type='STOCK')
    mock_get_item.side_effect = _lookup_by_asset_type(cash_item=cash, stock_item=stock)

    request = _request(type='buy', ticker='aapl', assetType='stock', quantity=10, price=150, useCash=True)
    result = TransactionService.record_transaction(request)

    assert mock_update_item.call_count == 2  # cash deduction + stock accumulation
    updated_cash, updated_stock = (call[0][0] for call in mock_update_item.call_args_list)
    assert updated_cash.quantity == 2000 - 1500  # 10 * 150
    assert updated_cash.costBasis == 2000 - 1500
    assert updated_stock.quantity == 5 + 10
    assert updated_stock.costBasis == 500 + 1500

    assert mock_add_txn.call_count == 2  # cash-side debit + the stock buy itself
    cash_txn, stock_txn = (call[0][0] for call in mock_add_txn.call_args_list)
    assert cash_txn.type == 'sell'
    assert cash_txn.quantity == 1500
    assert cash_txn.price == 1
    assert cash_txn.useCash is False

    assert stock_txn.type == 'buy'
    assert stock_txn.quantity == 10
    assert stock_txn.price == 150
    assert stock_txn.useCash is True
    assert result is stock_txn  # record_transaction returns the primary (stock) transaction


@patch('services.transaction_service.PortfolioItemRepository.update')
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')
def test_buy_asset_with_insufficient_cash_raises(mock_get_item, mock_update_item):
    mock_get_item.return_value = _cash_item(quantity=100, cost_basis=100)  # not enough for 10*150

    request = _request(type='buy', ticker='aapl', assetType='stock', quantity=10, price=150, useCash=True)
    with pytest.raises(InsufficientCashError):
        TransactionService.record_transaction(request)

    mock_update_item.assert_not_called()  # fails before any mutation happens


# --- record_transaction: REMOVE flow (type='sell') ------------------------------------------

@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)
@patch('services.transaction_service.PortfolioItemRepository.update')
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')
def test_withdraw_cash_success(mock_get_item, mock_update_item, mock_add_txn):
    mock_get_item.return_value = _cash_item(quantity=1000, cost_basis=1000)

    request = _request(type='sell', ticker='usd', assetType='cash', quantity=300, price=None)
    result = TransactionService.record_transaction(request)

    updated_item = mock_update_item.call_args[0][0]
    assert updated_item.quantity == 700
    assert updated_item.costBasis == 700

    assert result.type == 'sell'
    assert result.quantity == 300
    assert result.price == 1


@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')
def test_withdraw_cash_insufficient_raises(mock_get_item):
    mock_get_item.return_value = _cash_item(quantity=50, cost_basis=50)

    request = _request(type='sell', ticker='usd', assetType='cash', quantity=100, price=None)
    with pytest.raises(InsufficientCashError):
        TransactionService.record_transaction(request)


@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')
def test_sell_asset_not_found_raises(mock_get_item):
    mock_get_item.return_value = None  # AAPL doesn't exist

    request = _request(type='sell', ticker='aapl', assetType='stock', quantity=5, price=150)
    with pytest.raises(PortfolioItemNotFoundError):
        TransactionService.record_transaction(request)


@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')
def test_sell_asset_insufficient_quantity_raises(mock_get_item):
    mock_get_item.return_value = _item('AAPL', quantity=3, cost_basis=300, asset_type='STOCK')

    request = _request(type='sell', ticker='aapl', assetType='stock', quantity=5, price=150)
    with pytest.raises(InsufficientQuantityError):
        TransactionService.record_transaction(request)


@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)
@patch('services.transaction_service.PortfolioItemRepository.update')
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')
def test_sell_asset_credits_cash_and_reduces_cost_basis_proportionally(mock_get_item, mock_update_item, mock_add_txn):
    stock = _item('AAPL', quantity=10, cost_basis=1000, asset_type='STOCK')  # $100/share average
    cash = _cash_item(quantity=500, cost_basis=500)
    mock_get_item.side_effect = _lookup_by_asset_type(cash_item=cash, stock_item=stock)

    request = _request(type='sell', ticker='aapl', assetType='stock', quantity=4, price=120)
    result = TransactionService.record_transaction(request)

    updated_cash, updated_stock = (call[0][0] for call in mock_update_item.call_args_list)
    assert updated_cash.quantity == 500 + 480  # proceeds = 4 * 120
    assert updated_cash.costBasis == 500 + 480
    assert updated_stock.quantity == 6
    assert updated_stock.costBasis == 600  # $100/share average carried over 6 remaining shares

    cash_txn, stock_txn = (call[0][0] for call in mock_add_txn.call_args_list)
    assert cash_txn.type == 'buy'
    assert cash_txn.quantity == 480
    assert cash_txn.price == 1

    assert stock_txn.type == 'sell'
    assert stock_txn.quantity == 4
    assert stock_txn.price == 120
    assert stock_txn.useCash is True
    assert result is stock_txn


@patch('services.transaction_service.PortfolioItemRepository.delete')
@patch('services.transaction_service.TransactionRepository.add', side_effect=_fake_repo_add)
@patch('services.transaction_service.PortfolioItemRepository.update')
@patch('services.transaction_service.PortfolioItemRepository.get_by_ticker_and_asset_type')
def test_sell_asset_to_zero_quantity_keeps_item_instead_of_deleting(
    mock_get_item, mock_update_item, mock_add_txn, mock_delete_item,
):
    # transaction.portfolio_item_id is ON DELETE CASCADE, so deleting the item here would wipe
    # every transaction ever recorded against it - the item must be kept at quantity 0 instead
    stock = _item('AAPL', quantity=5, cost_basis=500, asset_type='STOCK')
    cash = _cash_item()
    mock_get_item.side_effect = _lookup_by_asset_type(cash_item=cash, stock_item=stock)

    request = _request(type='sell', ticker='aapl', assetType='stock', quantity=5, price=150)
    TransactionService.record_transaction(request)

    _, updated_stock = (call[0][0] for call in mock_update_item.call_args_list)
    assert updated_stock.quantity == 0
    assert updated_stock.costBasis == 0
    mock_delete_item.assert_not_called()
