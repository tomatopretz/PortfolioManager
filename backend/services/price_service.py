import logging
import math
import time
from datetime import date, datetime, timedelta

import yfinance as yf

logger = logging.getLogger(__name__)

# Yahoo Finance intermittently omits a subset of tickers from a yf.download() response
# (throttling/transient upstream hiccups), especially under repeated rapid requests. Retrying
# just the still-missing tickers a couple of times avoids treating a transient miss as "this
# holding has no price" (which would zero out its market value and drop it from the UI).
_MAX_ATTEMPTS = 3
_RETRY_BACKOFF_SECONDS = 0.3


class PriceNotFoundError(LookupError):
    """Raised when yfinance has no price data for a ticker (optionally on a given date)."""


def parse_tickers(tickers_param: str) -> list[str]:
    """Parse a comma-separated tickers string into a cleaned, upper-cased list."""
    return [t.strip().upper() for t in tickers_param.split(',') if t.strip()]


def _sanitize_price(value) -> float:
    """Round to cents and reject values that indicate corrupt/untrustworthy upstream data
    (NaN, +/-infinity, zero, negative) before it ever reaches a client."""
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f'implausible price value: {value}')
    return round(value, 2)


def list_current_prices(tickers: list[str]) -> dict[str, float]:
    """Get the latest available closing price for one or more tickers in a single request.

    Retries tickers that come back with no data, since Yahoo Finance can transiently omit a
    subset of tickers from a batch response rather than failing outright.
    """
    prices = {}
    remaining = list(tickers)

    for attempt in range(_MAX_ATTEMPTS):
        if not remaining:
            break
        if attempt > 0:
            time.sleep(_RETRY_BACKOFF_SECONDS)

        data = yf.download(remaining, period='1d', group_by='ticker', progress=False)
        still_missing = []
        for ticker in remaining:
            try:
                close = data[ticker]['Close'].iloc[-1]
                prices[ticker] = _sanitize_price(close)
            except (KeyError, IndexError, ValueError):
                still_missing.append(ticker)
        remaining = still_missing

    for ticker in remaining:
        logger.warning('Skipping ticker=%s: no data after %d attempts', ticker, _MAX_ATTEMPTS)

    return prices


def get_daily_price_history(tickers: list[str], start: date, end: date) -> dict[str, dict[date, float]]:
    """Get daily close prices for tickers between start and end, inclusive."""
    if not tickers:
        return {}

    data = yf.download(
        tickers,
        start=start,
        end=end + timedelta(days=1),
        interval='1d',
        group_by='ticker',
        auto_adjust=False,
        progress=False,
    )
    return _extract_close_history(data, tickers, key_type='date')


def get_intraday_price_history(
    tickers: list[str],
    period: str = '1d',
    interval: str = '5m',
) -> dict[str, dict[datetime, float]]:
    """Get intraday close prices for tickers."""
    if not tickers:
        return {}

    data = yf.download(
        tickers,
        period=period,
        interval=interval,
        group_by='ticker',
        auto_adjust=False,
        progress=False,
    )
    return _extract_close_history(data, tickers, key_type='datetime')


def _extract_close_history(data, tickers: list[str], key_type: str):
    """Normalize yfinance Close data into per-ticker date/datetime price maps."""
    prices = {}

    for ticker in tickers:
        try:
            close_series = _close_series_for_ticker(data, ticker, len(tickers) == 1)
        except KeyError:
            logger.warning('No close history for ticker=%s', ticker)
            prices[ticker] = {}
            continue

        ticker_prices = {}
        for index, close in close_series.dropna().items():
            try:
                clean_price = _sanitize_price(close)
            except ValueError:
                continue

            key = index.date() if key_type == 'date' else index.to_pydatetime()
            ticker_prices[key] = clean_price

        prices[ticker] = ticker_prices

    return prices


def _close_series_for_ticker(data, ticker: str, is_single_ticker: bool):
    if is_single_ticker:
        try:
            return data[ticker]['Close']
        except KeyError:
            return data['Close']

    return data[ticker]['Close']


def get_price_on_date(ticker: str, date: datetime) -> float:
    """Get the closing price for a ticker on a specific date."""
    next_day = date + timedelta(days=1)
    history = yf.Ticker(ticker).history(start=date, end=next_day)

    try:
        close = history['Close'].iloc[0]
        return _sanitize_price(close)
    except (KeyError, IndexError, ValueError) as e:
        logger.warning('No price data for ticker=%s date=%s: %s', ticker, date.date(), e)
        raise PriceNotFoundError(f"No price data found for '{ticker}' on {date.date()}") from None


def get_current_price(ticker: str) -> float:
    """Get the latest available closing price for a single ticker."""
    history = yf.Ticker(ticker).history(period='1d')

    try:
        close = history['Close'].iloc[-1]
        return _sanitize_price(close)
    except (KeyError, IndexError, ValueError) as e:
        logger.warning('No current price for ticker=%s: %s', ticker, e)
        raise PriceNotFoundError(f"No price data found for '{ticker}'") from None


def get_ticker_price(ticker: str, date: datetime | None = None) -> float:
    """Get the current price for a ticker, or its price on a specific date if `date` is given."""
    if date is None:
        return get_current_price(ticker)
    return get_price_on_date(ticker, date)


