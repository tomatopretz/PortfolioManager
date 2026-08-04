from bisect import bisect_right
from calendar import monthrange
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from models.PerformanceHistoryResultDTO import PerformanceHistoryResultDTO
from models.PerformancePointDTO import PerformancePointDTO
from services import price_service
from services.portfolio_service import PortfolioService
from services.transaction_service import TransactionService

CASH_TICKER = 'USD'
RANGE_KEYS = ('1D', '1W', '1M', '6M', '1Y', 'ALL')
DAILY_RANGE_MONTHS = {
    '1M': 1,
    '6M': 6,
    '1Y': 12,
}


# --- Public service -----------------------------------------------------------


class PerformanceService:
    """Business logic for chart-ready portfolio value history."""

    @staticmethod
    def get_performance() -> PerformanceHistoryResultDTO:
        """Return chart-ready portfolio value points for all supported ranges."""
        transactions = sorted(TransactionService.list_transactions(), key=lambda txn: txn.date)

        if not transactions:
            return PerformanceHistoryResultDTO(ranges={key: [] for key in RANGE_KEYS})

        items = PortfolioService.list_portfolio_items()
        tickers_by_item_id = _load_tickers_by_portfolio_item_id(items)
        current_holdings = _current_holdings_snapshot(items)
        priced_tickers = _priced_tickers(transactions, tickers_by_item_id)
        today = _today()
        now = _now()
        earliest_transaction_date = transactions[0].date.date()
        daily_start = min(earliest_transaction_date, _daily_range_start(today, '1Y'))

        daily_prices = price_service.get_daily_price_history(priced_tickers, daily_start, today)
        intraday_prices = price_service.get_intraday_price_history(priced_tickers)
        latest_value = _latest_intraday_value(current_holdings, intraday_prices, daily_prices, now)

        ranges = {
            '1D': _build_intraday_range(
                transactions,
                tickers_by_item_id,
                intraday_prices,
                daily_prices,
                current_holdings,
                now,
            ),
            '1W': _build_daily_range(
                transactions,
                tickers_by_item_id,
                daily_prices,
                current_holdings,
                latest_value,
                _daily_range_start(today, '1W'),
                today,
            ),
            '1M': _build_daily_range(
                transactions,
                tickers_by_item_id,
                daily_prices,
                current_holdings,
                latest_value,
                _daily_range_start(today, '1M'),
                today,
            ),
            '6M': _build_daily_range(
                transactions,
                tickers_by_item_id,
                daily_prices,
                current_holdings,
                latest_value,
                _daily_range_start(today, '6M'),
                today,
            ),
            '1Y': _build_daily_range(
                transactions,
                tickers_by_item_id,
                daily_prices,
                current_holdings,
                latest_value,
                _daily_range_start(today, '1Y'),
                today,
            ),
            'ALL': _build_daily_range(
                transactions,
                tickers_by_item_id,
                daily_prices,
                current_holdings,
                latest_value,
                earliest_transaction_date,
                today,
            ),
        }

        return PerformanceHistoryResultDTO(ranges=ranges)


# --- Clock and range helpers --------------------------------------------------


def _today() -> date:
    """Return today's date; isolated for deterministic tests."""
    return date.today()


def _now() -> datetime:
    """Return current UTC time as naive datetime for intraday comparisons."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _to_naive_utc(value: datetime) -> datetime:
    """yfinance intraday timestamps come back timezone-aware (exchange-local); transaction
    dates may or may not. Normalize both to naive UTC so they're comparable with `_now()`
    and with each other without raising on naive/aware mismatches."""
    if value.tzinfo is None:
        return value

    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _daily_range_start(today: date, range_key: str) -> date:
    """Return the inclusive daily start date for a supported chart range."""
    if range_key == '1W':
        return today - timedelta(days=7)

    return _subtract_months(today, DAILY_RANGE_MONTHS[range_key])


def _subtract_months(value: date, months: int) -> date:
    """Subtract calendar months while clamping to the destination month's last day."""
    month_index = value.year * 12 + value.month - 1 - months
    year = month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


# --- Portfolio snapshot helpers ----------------------------------------------


def _load_tickers_by_portfolio_item_id(items) -> dict[str, str]:
    """Map portfolio item IDs to normalized tickers for transaction replay."""
    return {item.id: _normalize_ticker(item.ticker) for item in items if item.id}


def _current_holdings_snapshot(items) -> dict[str, float]:
    """Build the current holdings quantity by ticker from portfolio items."""
    holdings = defaultdict(float)
    for item in items:
        if item is None or not item.id:
            continue

        ticker = _normalize_ticker(item.ticker)
        quantity = float(item.quantity or 0)
        if _is_cash_ticker(ticker):
            holdings[CASH_TICKER] += quantity
        elif quantity:
            holdings[ticker] += quantity

    return dict(holdings)


def _normalize_ticker(ticker: str | None) -> str:
    """Normalize a ticker for lookup and comparison."""
    return (ticker or '').upper()


def _is_cash_ticker(ticker: str | None) -> bool:
    """Return whether the ticker is the canonical cash ticker."""
    return _normalize_ticker(ticker) == CASH_TICKER


def _priced_tickers(transactions, tickers_by_item_id: dict[str, str]) -> list[str]:
    """Return non-cash tickers that need historical price data."""
    transaction_tickers = {
        ticker
        for txn in transactions
        for ticker in [tickers_by_item_id.get(txn.portfolioItemId)]
        if ticker and not _is_cash_ticker(ticker)
    }
    return sorted(transaction_tickers)


# --- Range builders -----------------------------------------------------------


def _build_daily_range(
    transactions,
    tickers_by_item_id: dict[str, str],
    daily_prices: dict[str, dict[date, float]],
    current_holdings: dict[str, float],
    latest_value: float | None,
    start_date: date,
    end_date: date,
) -> list[PerformancePointDTO]:
    """Build daily value points by walking current holdings backward through transactions."""
    points = []
    holdings = current_holdings.copy()
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
                value=latest_value
                if latest_value is not None and current_date == end_date
                else _calculate_value(holdings, daily_prices, price_indexes, current_date),
            )
        )
        current_date -= timedelta(days=1)

    return list(reversed(points))


def _build_intraday_range(
    transactions,
    tickers_by_item_id: dict[str, str],
    intraday_prices: dict[str, dict[datetime, float]],
    daily_prices: dict[str, dict[date, float]],
    current_holdings: dict[str, float],
    now: datetime,
) -> list[PerformancePointDTO]:
    """Chart the true last 24 hours: real bars while the market was open in that window,
    held flat off the last known price for any part of the window the market was closed.
    Holdings only move at the moment a transaction actually happened, so a stale/closed
    market never wipes out a same-day buy/sell just because there's no fresh price for it."""
    if not any(intraday_prices.values()):
        return []

    intraday_prices = _normalize_intraday_prices(intraday_prices)
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
    holdings = current_holdings.copy()
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


# --- Transaction replay -------------------------------------------------------


def _apply_transaction(holdings, txn, tickers_by_item_id: dict[str, str], reverse: bool = False) -> None:
    """Apply or reverse one transaction against a mutable holdings snapshot."""
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

    key = _normalize_ticker(ticker)
    holdings[key] = holdings.get(key, 0.0) + direction * txn.quantity


# --- Valuation helpers --------------------------------------------------------


def _latest_intraday_value(
    current_holdings: dict[str, float],
    intraday_prices: dict[str, dict[datetime, float]],
    daily_prices: dict[str, dict[date, float]],
    now: datetime,
) -> float | None:
    """Value current holdings with intraday prices, falling back to daily prices."""
    if not any(intraday_prices.values()):
        return None

    intraday_prices = _normalize_intraday_prices(intraday_prices)
    return _calculate_value(
        current_holdings,
        intraday_prices,
        _build_price_indexes(intraday_prices),
        now,
        fallback_price_history=daily_prices,
        fallback_price_indexes=_build_price_indexes(daily_prices),
    )


def _normalize_intraday_prices(intraday_prices: dict[str, dict[datetime, float]]) -> dict[str, dict[datetime, float]]:
    """Normalize intraday price timestamps to naive UTC for comparisons."""
    return {
        ticker: {_to_naive_utc(timestamp): price for timestamp, price in ticker_prices.items()}
        for ticker, ticker_prices in intraday_prices.items()
    }


def _calculate_value(
    holdings,
    price_history,
    price_indexes,
    target,
    fallback_price_history=None,
    fallback_price_indexes=None,
) -> float:
    """Value a holdings snapshot using the latest price at or before the target."""
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
    """Pre-sort price history keys so valuation can use binary search lookups."""
    return {ticker: sorted(prices.keys()) for ticker, prices in price_history.items()}


def _latest_price_on_or_before(price_map, sorted_keys, target):
    """Return the latest known price at or before the target date or timestamp."""
    index = bisect_right(sorted_keys, target) - 1
    if index < 0:
        return None

    return price_map[sorted_keys[index]]
