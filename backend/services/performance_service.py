from bisect import bisect_right
from collections import defaultdict
from datetime import date, datetime, timedelta

from models.PerformanceHistoryResultDTO import PerformanceHistoryResultDTO
from models.PerformancePointDTO import PerformancePointDTO
from services import price_service
from services.portfolio_item_service import PortfolioItemService
from services.transaction_service import TransactionService

CASH_TICKER = 'USD'
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
        if not transactions:
            return PerformanceHistoryResultDTO(ranges={key: [] for key in RANGE_KEYS})

        tickers_by_item_id = _load_tickers_by_portfolio_item_id()
        priced_tickers = _priced_tickers(transactions, tickers_by_item_id)
        today = _today()
        earliest_transaction_date = transactions[0].date.date()
        daily_start = min(earliest_transaction_date, today - timedelta(days=DAILY_RANGE_DAYS['1Y']))

        daily_prices = price_service.get_daily_price_history(priced_tickers, daily_start, today)
        intraday_prices = price_service.get_intraday_price_history(priced_tickers)

        ranges = {
            '1D': _build_intraday_range(transactions, tickers_by_item_id, intraday_prices),
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


def _load_tickers_by_portfolio_item_id() -> dict[str, str]:
    items = PortfolioItemService.list_portfolio_items()
    return {item.id: item.ticker.upper() for item in items if item.id}


def _is_cash_ticker(ticker: str | None) -> bool:
    return bool(ticker) and ticker.upper() == CASH_TICKER


def _priced_tickers(transactions, tickers_by_item_id: dict[str, str]) -> list[str]:
    return sorted({
        ticker
        for txn in transactions
        for ticker in [tickers_by_item_id.get(txn.portfolioItemId)]
        if ticker and not _is_cash_ticker(ticker)
    })


def _build_daily_range(
    transactions,
    tickers_by_item_id: dict[str, str],
    daily_prices: dict[str, dict[date, float]],
    start_date: date,
    end_date: date,
) -> list[PerformancePointDTO]:
    points = []
    holdings = defaultdict(float)
    sorted_transactions = sorted(transactions, key=lambda txn: txn.date)
    price_indexes = _build_price_indexes(daily_prices)
    txn_index = 0

    current_date = start_date
    while current_date <= end_date:
        while txn_index < len(sorted_transactions) and sorted_transactions[txn_index].date.date() <= current_date:
            _apply_transaction(holdings, sorted_transactions[txn_index], tickers_by_item_id)
            txn_index += 1

        points.append(
            PerformancePointDTO(
                date=current_date.isoformat(),
                value=_calculate_value(holdings, daily_prices, price_indexes, current_date),
            )
        )
        current_date += timedelta(days=1)

    return points


def _build_intraday_range(
    transactions,
    tickers_by_item_id: dict[str, str],
    intraday_prices: dict[str, dict[datetime, float]],
) -> list[PerformancePointDTO]:
    timestamps = sorted({
        timestamp
        for ticker_prices in intraday_prices.values()
        for timestamp in ticker_prices.keys()
    })
    if not timestamps:
        return []

    points = []
    sorted_transactions = sorted(transactions, key=lambda txn: txn.date)
    holdings = defaultdict(float)
    price_indexes = _build_price_indexes(intraday_prices)
    txn_index = 0

    for timestamp in timestamps:
        while txn_index < len(sorted_transactions) and sorted_transactions[txn_index].date <= timestamp:
            _apply_transaction(holdings, sorted_transactions[txn_index], tickers_by_item_id)
            txn_index += 1

        points.append(
            PerformancePointDTO(
                date=timestamp.isoformat(),
                value=_calculate_value(holdings, intraday_prices, price_indexes, timestamp),
            )
        )

    return points


def _apply_transaction(holdings, txn, tickers_by_item_id: dict[str, str]) -> None:
    ticker = tickers_by_item_id.get(txn.portfolioItemId)
    if not ticker:
        return

    transaction_type = txn.type.lower()
    direction = 1 if transaction_type == 'buy' else -1

    if _is_cash_ticker(ticker):
        holdings[CASH_TICKER] += direction * txn.quantity * txn.price
        return

    holdings[ticker] += direction * txn.quantity


def _calculate_value(holdings, price_history, price_indexes, target) -> float:
    total = holdings.get(CASH_TICKER, 0.0)

    for ticker, quantity in holdings.items():
        if ticker == CASH_TICKER or quantity <= 0:
            continue

        price = _latest_price_on_or_before(price_history.get(ticker, {}), price_indexes.get(ticker, []), target)
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
