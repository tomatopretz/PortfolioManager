import os
import sys
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.price_service import get_current_prices, get_price_on_date, parse_tickers, PriceNotFoundError


def _history_df(closes):
    return pd.DataFrame({'Close': closes})


def test_parse_tickers_splits_strips_and_upper_cases():
    assert parse_tickers(' aapl, goog ,tsla') == ['AAPL', 'GOOG', 'TSLA']


def test_parse_tickers_drops_empty_entries():
    assert parse_tickers('AAPL,,GOOG,') == ['AAPL', 'GOOG']


def test_parse_tickers_returns_empty_list_for_blank_input():
    assert parse_tickers('') == []


@patch('services.price_service.yf.Ticker')
def test_get_price_on_date_returns_close_for_that_day(mock_ticker):
    mock_ticker.return_value.history.return_value = _history_df([250.25])
    assert get_price_on_date('GOOG', datetime(2026, 7, 20)) == 250.25


@patch('services.price_service.yf.Ticker')
def test_get_price_on_date_raises_when_no_data(mock_ticker):
    mock_ticker.return_value.history.return_value = pd.DataFrame()
    with pytest.raises(PriceNotFoundError):
        get_price_on_date('GOOG', datetime(2026, 7, 20))


@patch('services.price_service.yf.download')
def test_get_current_prices_works_for_a_single_ticker(mock_download):
    columns = pd.MultiIndex.from_tuples([('AAPL', 'Close')])
    mock_download.return_value = pd.DataFrame([[105.5]], columns=columns)
    assert get_current_prices(['AAPL']) == {'AAPL': 105.5}


@patch('services.price_service.yf.download')
def test_get_current_prices_returns_prices_for_each_ticker(mock_download):
    columns = pd.MultiIndex.from_tuples([('AAPL', 'Close'), ('GOOG', 'Close')])
    mock_download.return_value = pd.DataFrame([[105.5, 250.25]], columns=columns)
    assert get_current_prices(['AAPL', 'GOOG']) == {'AAPL': 105.5, 'GOOG': 250.25}


@patch('services.price_service.yf.download')
def test_get_current_prices_skips_tickers_with_no_data(mock_download):
    columns = pd.MultiIndex.from_tuples([('AAPL', 'Close')])
    mock_download.return_value = pd.DataFrame([[105.5]], columns=columns)
    assert get_current_prices(['AAPL', 'BADTICKER']) == {'AAPL': 105.5}
