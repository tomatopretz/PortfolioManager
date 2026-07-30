import os
import sys
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.price_service import (
    get_current_price,
    list_current_prices,
    get_price_on_date,
    get_ticker_price,
    parse_tickers,
    PriceNotFoundError,
)


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


@patch('services.price_service.yf.Ticker')
def test_get_price_on_date_rounds_to_two_decimal_places(mock_ticker):
    mock_ticker.return_value.history.return_value = _history_df([340.0799865722656])
    assert get_price_on_date('AAPL', datetime(2026, 7, 20)) == 340.08


@pytest.mark.parametrize('bad_close', [float('nan'), float('inf'), float('-inf'), 0, -105.5])
@patch('services.price_service.yf.Ticker')
def test_get_price_on_date_raises_for_implausible_price(mock_ticker, bad_close):
    mock_ticker.return_value.history.return_value = _history_df([bad_close])
    with pytest.raises(PriceNotFoundError):
        get_price_on_date('AAPL', datetime(2026, 7, 20))


@patch('services.price_service.yf.download')
def test_list_current_prices_works_for_a_single_ticker(mock_download):
    columns = pd.MultiIndex.from_tuples([('AAPL', 'Close')])
    mock_download.return_value = pd.DataFrame([[105.5]], columns=columns)
    assert list_current_prices(['AAPL']) == {'AAPL': 105.5}


@patch('services.price_service.yf.download')
def test_list_current_prices_returns_prices_for_each_ticker(mock_download):
    columns = pd.MultiIndex.from_tuples([('AAPL', 'Close'), ('GOOG', 'Close')])
    mock_download.return_value = pd.DataFrame([[105.5, 250.25]], columns=columns)
    assert list_current_prices(['AAPL', 'GOOG']) == {'AAPL': 105.5, 'GOOG': 250.25}


@patch('services.price_service.yf.download')
def test_list_current_prices_skips_tickers_with_no_data(mock_download):
    columns = pd.MultiIndex.from_tuples([('AAPL', 'Close')])
    mock_download.return_value = pd.DataFrame([[105.5]], columns=columns)
    assert list_current_prices(['AAPL', 'BADTICKER']) == {'AAPL': 105.5}


@patch('services.price_service.yf.download')
def test_list_current_prices_rounds_to_two_decimal_places(mock_download):
    columns = pd.MultiIndex.from_tuples([('AAPL', 'Close')])
    mock_download.return_value = pd.DataFrame([[340.0799865722656]], columns=columns)
    assert list_current_prices(['AAPL']) == {'AAPL': 340.08}


@pytest.mark.parametrize('bad_close', [float('nan'), float('inf'), float('-inf'), 0, -105.5])
@patch('services.price_service.yf.download')
def test_list_current_prices_skips_implausible_prices(mock_download, bad_close):
    columns = pd.MultiIndex.from_tuples([('AAPL', 'Close')])
    mock_download.return_value = pd.DataFrame([[bad_close]], columns=columns)
    assert list_current_prices(['AAPL']) == {}


@patch('services.price_service.yf.Ticker')
def test_get_current_price_returns_latest_close(mock_ticker):
    mock_ticker.return_value.history.return_value = _history_df([182.19])
    assert get_current_price('AAPL') == 182.19


@patch('services.price_service.yf.Ticker')
def test_get_current_price_raises_when_no_data(mock_ticker):
    mock_ticker.return_value.history.return_value = pd.DataFrame()
    with pytest.raises(PriceNotFoundError):
        get_current_price('BADTICKER')


@patch('services.price_service.get_current_price')
def test_get_ticker_price_uses_current_price_when_no_date(mock_get_current_price):
    mock_get_current_price.return_value = 105.5
    assert get_ticker_price('AAPL') == 105.5
    mock_get_current_price.assert_called_once_with('AAPL')


@patch('services.price_service.get_price_on_date')
def test_get_ticker_price_uses_price_on_date_when_date_given(mock_get_price_on_date):
    mock_get_price_on_date.return_value = 99.0
    date = datetime(2026, 7, 20)
    assert get_ticker_price('AAPL', date) == 99.0
    mock_get_price_on_date.assert_called_once_with('AAPL', date)
