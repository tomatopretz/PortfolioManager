from bisect import bisect_right
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from models.PerformanceHistoryResultDTO import PerformanceHistoryResultDTO
from models.PerformancePointDTO import PerformancePointDTO
from services import price_service
from services.portfolio_service import PortfolioService
from services.transaction_service import TransactionService

CASH_TICKER = 'USD'
CASH_TICKERS = {'CASH', 'USD'}
CASH_ASSET_TYPE = 'CASH'
RANGE_KEYS = ('1D', '1W', '1M', '6M', '1Y', 'ALL')
DAILY_RANGE_DAYS = {
    '1W': 7,
    '1M': 30,
    '6M': 182,
    '1Y': 365,
}


class PerformanceService:
    """Business logic for chart-ready portfolio value history."""

    @staticmethod
    def get_performance() -> PerformanceHistoryResultDTO:
        transactions = sorted(TransactionService.list_transactions(), key=lambda txn: txn.date)
        tickers_by_item_id = _load_tickers_by_portfolio_item_id()
        current_snapshot = _current_holdings_snapshot()

        if not transactions:
            if not current_snapshot:
                return PerformanceHistoryResultDTO(ranges={key: [] for key in RANGE_KEYS})

            today = _today()
            range_points = [
                PerformancePointDTO(date=today.isoformat(), value=_value_from_current_prices(current_snapshot))
            ]
            return PerformanceHistoryResultDTO(ranges={key: range_points.copy() for key in RANGE_KEYS})

        priced_tickers = _priced_tickers(transactions, tickers_by_item_id)
        today = _today()
        now = _now()
        earliest_transaction_date = transactions[0].date.date()
        daily_start = min(earliest_transaction_date, today - timedelta(days=DAILY_RANGE_DAYS['1Y']))

        daily_prices = price_service.get_daily_price_history(priced_tickers, daily_start, today)
        intraday_prices = price_service.get_intraday_price_history(priced_tickers)

        ranges = {
            '1D': _build_intraday_range(transactions, tickers_by_item_id, intraday_prices, daily_prices, now),
            '1W': _build_daily_range(
                transactions,
                tickers_by_item_id,
                daily_prices,
                today - timedelta(days=DAILY_RANGE_DAYS['1W']),
                today,
            ),
            '1M': _build_daily_range(
                transactions,
                tickers_by_item_id,
                daily_prices,
                today - timedelta(days=DAILY_RANGE_DAYS['1M']),
                today,
            ),
            '6M': _build_daily_range(
                transactions,
                tickers_by_item_id,
                daily_prices,
                today - timedelta(days=DAILY_RANGE_DAYS['6M']),
                today,
            ),
            '1Y': _build_daily_range(
                transactions,
                tickers_by_item_id,
                daily_prices,
                today - timedelta(days=DAILY_RANGE_DAYS['1Y']),
                today,
            ),
            'ALL': _build_daily_range(
                transactions,
                tickers_by_item_id,
                daily_prices,
                earliest_transaction_date,
                today,
            ),
        }

        return PerformanceHistoryResultDTO(ranges=ranges)


def _today() -> date:
    return date.today()


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _to_naive_utc(value: datetime) -> datetime:
    """yfinance intraday timestamps come back timezone-aware (exchange-local); transaction
    dates may or may not. Normalize both to naive UTC so they're comparable with `_now()`
    and with each other without raising on naive/aware mismatches."""
    if value.tzinfo is None:
        return value

    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _value_from_current_prices(holdings: dict[str, float]) -> float:
    non_cash_tickers = sorted(ticker for ticker in holdings if ticker != CASH_TICKER)
    current_prices = price_service.list_current_prices(non_cash_tickers) if non_cash_tickers else {}

    total = holdings.get(CASH_TICKER, 0.0)
    for ticker in non_cash_tickers:
        price = current_prices.get(ticker)
        if price is not None:
            total += holdings[ticker] * price

    return round(total, 2)


def _load_tickers_by_portfolio_item_id() -> dict[str, str]:
    items = PortfolioService.list_portfolio_items()
    return {item.id: (_normalize_cash_ticker(item.ticker) if item.ticker else '') for item in items if item.id}


def _current_holdings_snapshot() -> dict[str, float]:
    holdings = defaultdict(float)
    for item in PortfolioService.list_portfolio_items():
        if item is None or not item.id:
            continue

        ticker = _normalize_cash_ticker(item.ticker)
        quantity = float(item.quantity or 0)
        if _is_cash_ticker(ticker):
            holdings[CASH_TICKER] += quantity
        elif quantity:
            holdings[ticker] += quantity

    return dict(holdings)


def _normalize_cash_ticker(ticker: str | None) -> str:
    ticker = (ticker or '').upper()
    return CASH_TICKER if ticker in CASH_TICKERS else ticker


def _is_cash_ticker(ticker: str | None) -> bool:
    return bool(ticker) and _normalize_cash_ticker(ticker) == CASH_TICKER


def _priced_tickers(transactions, tickers_by_item_id: dict[str, str]) -> list[str]:
    item_tickers = {
        _normalize_cash_ticker(item.ticker)
        for item in PortfolioService.list_portfolio_items()
        if item and item.ticker and not _is_cash_ticker(item.ticker)
    }
    transaction_tickers = {
        ticker
        for txn in transactions
        for ticker in [tickers_by_item_id.get(txn.portfolioItemId)]
        if ticker and not _is_cash_ticker(ticker)
    }
    return sorted(item_tickers | transaction_tickers)


def _build_daily_range(
    transactions,
    tickers_by_item_id: dict[str, str],
    daily_prices: dict[str, dict[date, float]],
    start_date: date,
    end_date: date,
) -> list[PerformancePointDTO]:
    points = []
    holdings = _current_holdings_snapshot()
    sorted_transactions = sorted(transactions, key=lambda txn: txn.date)
    price_indexes = _build_price_indexes(daily_prices)
    txn_index = len(sorted_transactions) - 1

    current_date = end_date
    while current_date >= start_date:
        while txn_index >= 0 and sorted_transactions[txn_index].date.date() > current_date:
            _apply_transaction(holdings, sorted_transactions[txn_index], tickers_by_item_id, reverse=True)
            txn_index -= 1

        points.append(
            PerformancePointDTO(
                date=current_date.isoformat(),
                value=_calculate_value(holdings, daily_prices, price_indexes, current_date),
            )
        )
        current_date -= timedelta(days=1)

    return list(reversed(points))


def _build_intraday_range(
    transactions,
    tickers_by_item_id: dict[str, str],
    intraday_prices: dict[str, dict[datetime, float]],
    daily_prices: dict[str, dict[date, float]],
    now: datetime,
) -> list[PerformancePointDTO]:
    """Chart the true last 24 hours: real bars while the market was open in that window,
    held flat off the last known price for any part of the window the market was closed.
    Holdings only move at the moment a transaction actually happened, so a stale/closed
    market never wipes out a same-day buy/sell just because there's no fresh price for it."""
    if not any(intraday_prices.values()):
        return []

    intraday_prices = {
        ticker: {_to_naive_utc(timestamp): price for timestamp, price in ticker_prices.items()}
        for ticker, ticker_prices in intraday_prices.items()
    }
    window_start = now - timedelta(hours=24)

    bar_timestamps = {
        timestamp
        for ticker_prices in intraday_prices.values()
        for timestamp in ticker_prices.keys()
        if timestamp >= window_start
    }

    sorted_transactions = sorted(transactions, key=lambda txn: _to_naive_utc(txn.date))
    txn_dates = [_to_naive_utc(txn.date) for txn in sorted_transactions]
    txn_timestamps = {txn_date for txn_date in txn_dates if window_start <= txn_date <= now}
    timestamps = sorted(bar_timestamps | txn_timestamps | {window_start, now})

    points = []
    holdings = _current_holdings_snapshot()
    intraday_price_indexes = _build_price_indexes(intraday_prices)
    daily_price_indexes = _build_price_indexes(daily_prices)
    txn_index = len(sorted_transactions) - 1

    for timestamp in reversed(timestamps):
        while txn_index >= 0 and txn_dates[txn_index] > timestamp:
            _apply_transaction(holdings, sorted_transactions[txn_index], tickers_by_item_id, reverse=True)
            txn_index -= 1

        points.append(
            PerformancePointDTO(
                # timestamp is naive but was normalized to UTC above; mark it explicitly so
                # the client doesn't parse it as its own local time.
                date=timestamp.isoformat() + 'Z',
                value=_calculate_value(
                    holdings,
                    intraday_prices,
                    intraday_price_indexes,
                    timestamp,
                    fallback_price_history=daily_prices,
                    fallback_price_indexes=daily_price_indexes,
                ),
            )
        )

    return list(reversed(points))


def _apply_transaction(holdings, txn, tickers_by_item_id: dict[str, str], reverse: bool = False) -> None:
    ticker = tickers_by_item_id.get(txn.portfolioItemId)
    if not ticker:
        return

    transaction_type = txn.type.lower()
    direction = 1 if transaction_type == 'buy' else -1
    if reverse:
        direction *= -1

    if _is_cash_ticker(ticker):
        key = CASH_TICKER
        holdings[key] = holdings.get(key, 0.0) + direction * txn.quantity * txn.price
        return

    key = _normalize_cash_ticker(ticker)
    holdings[key] = holdings.get(key, 0.0) + direction * txn.quantity


def _calculate_value(
    holdings,
    price_history,
    price_indexes,
    target,
    fallback_price_history=None,
    fallback_price_indexes=None,
) -> float:
    total = holdings.get(CASH_TICKER, 0.0)
    fallback_date = target.date() if hasattr(target, 'date') else target

    for ticker, quantity in holdings.items():
        if ticker == CASH_TICKER or quantity <= 0:
            continue

        price = _latest_price_on_or_before(price_history.get(ticker, {}), price_indexes.get(ticker, []), target)
        if price is None and fallback_price_history is not None:
            price = _latest_price_on_or_before(
                fallback_price_history.get(ticker, {}),
                fallback_price_indexes.get(ticker, []),
                fallback_date,
            )

        if price is not None:
            total += quantity * price

    return round(total, 2)


def _build_price_indexes(price_history) -> dict:
    return {ticker: sorted(prices.keys()) for ticker, prices in price_history.items()}


def _latest_price_on_or_before(price_map, sorted_keys, target):
    index = bisect_right(sorted_keys, target) - 1
    if index < 0:
        return None

    return price_map[sorted_keys[index]]
