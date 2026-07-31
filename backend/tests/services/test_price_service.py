import os
import sys
from datetime import date, datetime, timedelta
from unittest.mock import patch

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.price_service import (
    get_current_price,
    get_daily_price_history,
    get_intraday_price_history,
    list_current_prices,
    get_price_on_date,
    get_ticker_price,
    parse_tickers,
    PriceNotFoundError,
)


def _history_df(closes):
    return pd.DataFrame({'Close': closes})


def _download_df(closes_by_ticker):
    columns = pd.MultiIndex.from_tuples((ticker, 'Close') for ticker in closes_by_ticker)
    index = pd.to_datetime(['2026-07-30', '2026-07-31'])
    rows = [
        [closes[0] for closes in closes_by_ticker.values()],
        [closes[1] for closes in closes_by_ticker.values()],
    ]
    return pd.DataFrame(rows, index=index, columns=columns)


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


@patch('services.price_service.yf.download')
def test_get_daily_price_history_returns_close_prices_by_date(mock_download):
    mock_download.return_value = _download_df({'AAPL': [190.123, 191.0], 'MSFT': [500.0, 505.0]})

    result = get_daily_price_history(['AAPL', 'MSFT'], date(2026, 7, 30), date(2026, 7, 31))

    assert result == {
        'AAPL': {date(2026, 7, 30): 190.12, date(2026, 7, 31): 191.0},
        'MSFT': {date(2026, 7, 30): 500.0, date(2026, 7, 31): 505.0},
    }
    mock_download.assert_called_once_with(
        ['AAPL', 'MSFT'],
        start=date(2026, 7, 30),
        end=date(2026, 8, 1),
        interval='1d',
        group_by='ticker',
        auto_adjust=False,
        progress=False,
    )


@patch('services.price_service.yf.download')
def test_get_daily_price_history_handles_single_ticker_dataframe(mock_download):
    index = pd.to_datetime(['2026-07-30', '2026-07-31'])
    mock_download.return_value = pd.DataFrame({'Close': [190.0, 191.0]}, index=index)

    result = get_daily_price_history(['AAPL'], date(2026, 7, 30), date(2026, 7, 31))

    assert result == {'AAPL': {date(2026, 7, 30): 190.0, date(2026, 7, 31): 191.0}}


@patch('services.price_service.yf.download')
def test_get_intraday_price_history_returns_close_prices_by_timestamp(mock_download):
    timestamps = pd.to_datetime(['2026-07-31 09:30:00', '2026-07-31 09:35:00'])
    columns = pd.MultiIndex.from_tuples([('AAPL', 'Close')])
    mock_download.return_value = pd.DataFrame([[190.0], [191.0]], index=timestamps, columns=columns)

    result = get_intraday_price_history(['AAPL'])

    assert result == {
        'AAPL': {
            datetime(2026, 7, 31, 9, 30): 190.0,
            datetime(2026, 7, 31, 9, 35): 191.0,
        }
    }
    mock_download.assert_called_once_with(
        ['AAPL'],
        period='1d',
        interval='5m',
        group_by='ticker',
        auto_adjust=False,
        progress=False,
    )


@patch('services.price_service.yf.download')
def test_get_daily_price_history_skips_implausible_prices(mock_download):
    columns = pd.MultiIndex.from_tuples([('AAPL', 'Close')])
    index = pd.to_datetime(['2026-07-30', '2026-07-31'])
    mock_download.return_value = pd.DataFrame([[float('nan')], [191.0]], index=index, columns=columns)

    assert get_daily_price_history(['AAPL'], date(2026, 7, 30), date(2026, 7, 31)) == {
        'AAPL': {date(2026, 7, 31): 191.0}
    }


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
