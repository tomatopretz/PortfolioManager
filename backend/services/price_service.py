import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


class PriceNotFoundError(LookupError):
    """Raised when yfinance has no price data for a ticker (optionally on a given date)."""


def parse_tickers(tickers_param: str) -> list[str]:
    """Parse a comma-separated tickers string into a cleaned, upper-cased list."""
    return [t.strip().upper() for t in tickers_param.split(',') if t.strip()]


def get_current_prices(tickers: list[str]) -> dict[str, float]:
    """Get the latest available closing price for one or more tickers in a single request."""
    data = yf.download(tickers, period='1d', group_by='ticker', progress=False)
    prices = {}
    for ticker in tickers:
        try:
            close = data[ticker]['Close'].iloc[-1]
        except (KeyError, IndexError):
            continue
        if not pd.isna(close):
            prices[ticker] = float(close)
    return prices


def get_price_on_date(ticker: str, date: datetime) -> float:
    """Get the closing price for a ticker on a specific date."""
    next_day = date + timedelta(days=1)
    history = yf.Ticker(ticker).history(start=date, end=next_day)
    if history.empty:
        raise PriceNotFoundError(f"No price data found for '{ticker}' on {date.date()}")
    return float(history['Close'].iloc[0])
