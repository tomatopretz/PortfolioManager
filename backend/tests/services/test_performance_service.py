import os
import sys
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.PortfolioItemDTO import PortfolioItemDTO
from models.TransactionDTO import TransactionDTO
from services.performance_service import PerformanceService

AAPL_ID = '11111111-1111-4111-8111-111111111111'
MSFT_ID = '22222222-2222-4222-8222-222222222222'
CASH_ID = '33333333-3333-4333-8333-333333333333'


def _item(item_id, ticker, quantity=0):
    return PortfolioItemDTO(
        id=item_id,
        ticker=ticker,
        assetType='cash' if ticker == 'CASH' else 'stock',
        quantity=quantity,
        costBasis=0,
    )


def _txn(item_id, txn_type, quantity, price, txn_date):
    return TransactionDTO(
        id=None,
        portfolioItemId=item_id,
        type=txn_type,
        quantity=quantity,
        price=price,
        date=txn_date,
        useCash=True,
    )


# mock: replaces "now"/"today", current holdings, transaction history, and both yfinance-backed
# price-history lookups, so get_performance() runs on fully controlled fake data with no real
# clock, DB, or network call
@patch('services.performance_service._now')
@patch('services.performance_service.price_service.get_intraday_price_history')
@patch('services.performance_service.price_service.get_daily_price_history')
@patch('services.performance_service.PortfolioService.list_portfolio_items')
@patch('services.performance_service.TransactionService.list_transactions')
@patch('services.performance_service._today')
def test_get_performance_reconstructs_buy_sell_mixed_history_with_cash(
    mock_today,
    mock_list_transactions,
    mock_list_items,
    mock_daily_prices,
    mock_intraday_prices,
    mock_now,
):
    # Given a mix of buys/sells across AAPL, MSFT, and CASH, plus daily/intraday prices for them
    mock_today.return_value = date(2026, 7, 31)
    mock_now.return_value = datetime(2026, 7, 31, 9, 35)
    mock_list_items.return_value = [
        _item(AAPL_ID, 'AAPL', quantity=6),  # 10 bought - 4 sold
        _item(MSFT_ID, 'MSFT', quantity=2),
        _item(CASH_ID, 'USD', quantity=440),
    ]
    mock_list_transactions.return_value = [
        _txn(AAPL_ID, 'buy', 10, 100, datetime(2026, 7, 28, 10)),
        _txn(AAPL_ID, 'sell', 4, 110, datetime(2026, 7, 29, 10)),
        _txn(CASH_ID, 'buy', 440, 1, datetime(2026, 7, 29, 10)),
        _txn(MSFT_ID, 'buy', 2, 50, datetime(2026, 7, 30, 10)),
    ]
    mock_daily_prices.return_value = {
        'AAPL': {
            date(2026, 7, 28): 100,
            date(2026, 7, 29): 110,
            date(2026, 7, 30): 120,
            date(2026, 7, 31): 125,
        },
        'MSFT': {
            date(2026, 7, 30): 50,
            date(2026, 7, 31): 60,
        },
    }
    mock_intraday_prices.return_value = {
        'AAPL': {
            datetime(2026, 7, 31, 9, 30): 126,
            datetime(2026, 7, 31, 9, 35): 127,
        },
        'MSFT': {
            datetime(2026, 7, 31, 9, 30): 61,
            datetime(2026, 7, 31, 9, 35): 62,
        },
    }

    # When computing performance history
    result = PerformanceService.get_performance()

    # Then all six ranges exist, and the ALL/1D series correctly reconstruct portfolio value
    # over time from the reverse-replayed transaction history
    assert set(result.ranges.keys()) == {'1D', '1W', '1M', '6M', '1Y', 'ALL'}
    assert [(point.date, point.value) for point in result.ranges['ALL']] == [
        ('2026-07-28', 1000.0),
        ('2026-07-29', 1100.0),
        ('2026-07-30', 1260.0),
        ('2026-07-31', 1310.0),
    ]
    assert [(point.date, point.value) for point in result.ranges['1D']] == [
        ('2026-07-30T09:35:00Z', 1160.0),
        ('2026-07-30T10:00:00Z', 1260.0),
        ('2026-07-31T09:30:00Z', 1318.0),
        ('2026-07-31T09:35:00Z', 1326.0),
    ]
    mock_daily_prices.assert_called_once_with(['AAPL', 'MSFT'], date(2025, 7, 31), date(2026, 7, 31))
    mock_intraday_prices.assert_called_once_with(['AAPL', 'MSFT'])


# mock: replaces "now"/"today", current holdings, transaction history, and both yfinance-backed
# price-history lookups, so get_performance() runs on fully controlled fake data with no real
# clock, DB, or network call
@patch('services.performance_service._now')
@patch('services.performance_service.price_service.get_intraday_price_history')
@patch('services.performance_service.price_service.get_daily_price_history')
@patch('services.performance_service.PortfolioService.list_portfolio_items')
@patch('services.performance_service.TransactionService.list_transactions')
@patch('services.performance_service._today')
def test_get_performance_1d_holds_price_flat_while_market_closed_but_still_counts_new_buys(
    mock_today,
    mock_list_transactions,
    mock_list_items,
    mock_daily_prices,
    mock_intraday_prices,
    mock_now,
):
    """Market's been closed since Friday's 15:55 close; it's now Monday 9am, before the open.
    A stock bought at 8am Monday must still show up in the 1D chart even though there's no
    fresh price for it yet - and prices for existing holdings must stay flat, not replay
    Friday's now-stale intraday swings as if they happened in the last 24 hours."""
    # Given it's Monday 9am (pre-open), AAPL was bought before Friday's close, MSFT was bought
    # this morning, and only Friday's stale intraday AAPL prices exist
    mock_today.return_value = date(2026, 8, 3)
    mock_now.return_value = datetime(2026, 8, 3, 9, 0)
    mock_list_items.return_value = [
        _item(AAPL_ID, 'AAPL', quantity=10),
        _item(MSFT_ID, 'MSFT', quantity=5),
    ]
    mock_list_transactions.return_value = [
        _txn(AAPL_ID, 'buy', 10, 130, datetime(2026, 7, 20, 10)),
        _txn(MSFT_ID, 'buy', 5, 180, datetime(2026, 8, 3, 8, 0)),
    ]
    mock_daily_prices.return_value = {
        'AAPL': {date(2026, 7, 31): 142.0},
        'MSFT': {date(2026, 7, 31): 180.0},
    }
    mock_intraday_prices.return_value = {
        'AAPL': {
            datetime(2026, 7, 31, 9, 30): 140.0,
            datetime(2026, 7, 31, 15, 55): 142.0,
        },
    }

    # When computing performance history
    result = PerformanceService.get_performance()

    # Then the 1D chart holds AAPL's price flat at Friday's close (no stale intraday replay) and
    # still reflects this morning's MSFT buy
    assert [(point.date, point.value) for point in result.ranges['1D']] == [
        ('2026-08-02T09:00:00Z', 1420.0),
        ('2026-08-03T08:00:00Z', 2320.0),
        ('2026-08-03T09:00:00Z', 2320.0),
    ]


# mock: replaces "now"/"today", current holdings, transaction history, and both yfinance-backed
# price-history lookups, so get_performance() runs on fully controlled fake data with no real
# clock, DB, or network call
@patch('services.performance_service._now')
@patch('services.performance_service.price_service.get_intraday_price_history')
@patch('services.performance_service.price_service.get_daily_price_history')
@patch('services.performance_service.PortfolioService.list_portfolio_items')
@patch('services.performance_service.TransactionService.list_transactions')
@patch('services.performance_service._today')
def test_get_performance_1d_handles_timezone_aware_intraday_timestamps(
    mock_today,
    mock_list_transactions,
    mock_list_items,
    mock_daily_prices,
    mock_intraday_prices,
    mock_now,
):
    """yfinance returns intraday timestamps as timezone-aware (exchange-local, e.g. US/Eastern
    UTC-4), while `_now()` and transaction dates are naive. Mixing them must not raise
    TypeError, and the aware timestamps must still convert correctly for windowing/lookup."""
    # Given intraday prices with UTC-4 (US/Eastern) timezone-aware timestamps
    eastern = timezone(timedelta(hours=-4))
    mock_today.return_value = date(2026, 8, 3)
    mock_now.return_value = datetime(2026, 8, 3, 9, 0)
    mock_list_items.return_value = [_item(AAPL_ID, 'AAPL', quantity=10)]
    mock_list_transactions.return_value = [
        _txn(AAPL_ID, 'buy', 10, 130, datetime(2026, 7, 20, 10)),
    ]
    mock_daily_prices.return_value = {'AAPL': {date(2026, 7, 31): 142.0}}
    mock_intraday_prices.return_value = {
        'AAPL': {
            datetime(2026, 7, 31, 9, 30, tzinfo=eastern): 140.0,
            datetime(2026, 7, 31, 15, 55, tzinfo=eastern): 142.0,
        },
    }

    # When/Then computing performance history doesn't raise, and the aware timestamps still
    # convert and window correctly against the naive "now"
    result = PerformanceService.get_performance()

    assert [(point.date, point.value) for point in result.ranges['1D']] == [
        ('2026-08-02T09:00:00Z', 1420.0),
        ('2026-08-03T09:00:00Z', 1420.0),
    ]


# mock: replaces current holdings, transaction history, and both yfinance-backed price-history
# lookups, so get_performance() runs on fully controlled fake data with no real DB/network call
@patch('services.performance_service.price_service.get_intraday_price_history')
@patch('services.performance_service.price_service.get_daily_price_history')
@patch('services.performance_service.PortfolioService.list_portfolio_items')
@patch('services.performance_service.TransactionService.list_transactions')
@patch('services.performance_service._today')
def test_get_performance_uses_previous_close_for_non_trading_days(
    mock_today,
    mock_list_transactions,
    mock_list_items,
    mock_daily_prices,
    mock_intraday_prices,
):
    # Given a buy on 7/30 but no price data at all for 7/31 (e.g. a weekend/holiday)
    mock_today.return_value = date(2026, 7, 31)
    mock_list_items.return_value = [_item(AAPL_ID, 'AAPL', quantity=2)]
    mock_list_transactions.return_value = [_txn(AAPL_ID, 'buy', 2, 100, datetime(2026, 7, 30, 10))]
    mock_daily_prices.return_value = {'AAPL': {date(2026, 7, 30): 100}}
    mock_intraday_prices.return_value = {}

    # When/Then 7/31's point carries forward 7/30's closing value instead of dropping the date
    result = PerformanceService.get_performance()

    assert [(point.date, point.value) for point in result.ranges['ALL']] == [
        ('2026-07-30', 200.0),
        ('2026-07-31', 200.0),
    ]


# mock: replaces current holdings, transaction history, and both yfinance-backed price-history
# lookups, so get_performance() runs on fully controlled fake data with no real DB/network call
@patch('services.performance_service.price_service.get_intraday_price_history')
@patch('services.performance_service.price_service.get_daily_price_history')
@patch('services.performance_service.PortfolioService.list_portfolio_items')
@patch('services.performance_service.TransactionService.list_transactions')
@patch('services.performance_service._today')
def test_get_performance_handles_cash_only_history(
    mock_today,
    mock_list_transactions,
    mock_list_items,
    mock_daily_prices,
    mock_intraday_prices,
):
    # Given a portfolio holding only CASH (a deposit followed by a partial withdrawal)
    mock_today.return_value = date(2026, 7, 31)
    mock_list_items.return_value = [_item(CASH_ID, 'USD', quantity=750)]  # 1000 deposited - 250 withdrawn
    mock_list_transactions.return_value = [
        _txn(CASH_ID, 'buy', 1000, 1, datetime(2026, 7, 30, 10)),
        _txn(CASH_ID, 'sell', 250, 1, datetime(2026, 7, 31, 10)),
    ]
    mock_daily_prices.return_value = {}
    mock_intraday_prices.return_value = {}

    # When/Then the value history tracks the CASH balance directly, with no price lookups at all
    result = PerformanceService.get_performance()

    assert [(point.date, point.value) for point in result.ranges['ALL']] == [
        ('2026-07-30', 1000.0),
        ('2026-07-31', 750.0),
    ]
    mock_daily_prices.assert_called_once_with([], date(2025, 7, 31), date(2026, 7, 31))
    mock_intraday_prices.assert_called_once_with([])


# mock: replaces current holdings, transaction history, and both yfinance-backed price-history
# lookups, so get_performance() runs on fully controlled fake data with no real DB/network call
@patch('services.performance_service.price_service.get_intraday_price_history')
@patch('services.performance_service.price_service.get_daily_price_history')
@patch('services.performance_service.PortfolioService.list_portfolio_items')
@patch('services.performance_service.TransactionService.list_transactions')
@patch('services.performance_service._today')
def test_get_performance_treats_usd_as_cash_when_building_history(
    mock_today,
    mock_list_transactions,
    mock_list_items,
    mock_daily_prices,
    mock_intraday_prices,
):
    # Given the CASH item, keyed by its USD ticker rather than an assetType check
    mock_today.return_value = date(2026, 7, 31)
    mock_list_items.return_value = [_item(CASH_ID, 'USD', quantity=750)]
    mock_list_transactions.return_value = [
        _txn(CASH_ID, 'buy', 1000, 1, datetime(2026, 7, 30, 10)),
        _txn(CASH_ID, 'sell', 250, 1, datetime(2026, 7, 31, 10)),
    ]
    mock_daily_prices.return_value = {}
    mock_intraday_prices.return_value = {}

    # When/Then it's still recognized and priced as cash, with no price lookups needed
    result = PerformanceService.get_performance()

    assert [(point.date, point.value) for point in result.ranges['ALL']] == [
        ('2026-07-30', 1000.0),
        ('2026-07-31', 750.0),
    ]
    mock_daily_prices.assert_called_once_with([], date(2025, 7, 31), date(2026, 7, 31))
    mock_intraday_prices.assert_called_once_with([])


# mock: replaces current holdings, transaction history, both yfinance-backed price-history
# lookups, and the current-price lookup, so get_performance() runs on fully controlled fake data
# with no real DB/network call
@patch('services.performance_service.price_service.list_current_prices')
@patch('services.performance_service.price_service.get_intraday_price_history')
@patch('services.performance_service.price_service.get_daily_price_history')
@patch('services.performance_service.PortfolioService.list_portfolio_items')
@patch('services.performance_service.TransactionService.list_transactions')
@patch('services.performance_service._today')
def test_get_performance_values_current_holdings_by_market_price_when_no_transactions(
    mock_today,
    mock_list_transactions,
    mock_list_items,
    mock_daily_prices,
    mock_intraday_prices,
    mock_current_prices,
):
    # Given holdings exist but there's no transaction history to reconstruct from at all
    mock_today.return_value = date(2026, 7, 31)
    mock_list_transactions.return_value = []
    mock_list_items.return_value = [_item(AAPL_ID, 'AAPL', quantity=10), _item(CASH_ID, 'USD', quantity=500)]
    mock_current_prices.return_value = {'AAPL': 125.0}

    # When/Then it falls back to valuing today's holdings at the current market price instead of
    # trying (and failing) to replay history
    result = PerformanceService.get_performance()

    assert [(point.date, point.value) for point in result.ranges['ALL']] == [
        ('2026-07-31', 1750.0),
    ]
    mock_daily_prices.assert_not_called()
    mock_intraday_prices.assert_not_called()
    mock_current_prices.assert_called_once_with(['AAPL'])


# mock: replaces current holdings, transaction history, and both yfinance-backed price-history
# lookups, so get_performance() runs on fully controlled fake data with no real DB/network call
@patch('services.performance_service.price_service.get_intraday_price_history')
@patch('services.performance_service.price_service.get_daily_price_history')
@patch('services.performance_service.PortfolioService.list_portfolio_items')
@patch('services.performance_service.TransactionService.list_transactions')
def test_get_performance_returns_empty_ranges_for_empty_transaction_history(
    mock_list_transactions,
    mock_list_items,
    mock_daily_prices,
    mock_intraday_prices,
):
    # Given a completely empty portfolio (no holdings, no transactions)
    mock_list_transactions.return_value = []
    mock_list_items.return_value = []

    # When/Then every range comes back as [] rather than raising or fetching any prices
    result = PerformanceService.get_performance()

    assert result.ranges == {'1D': [], '1W': [], '1M': [], '6M': [], '1Y': [], 'ALL': []}
    mock_daily_prices.assert_not_called()
    mock_intraday_prices.assert_not_called()
