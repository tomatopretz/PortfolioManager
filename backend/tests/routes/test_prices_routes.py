import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app
from services.price_service import PriceNotFoundError


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('routes.prices.price_service.get_current_prices')
def test_get_current_prices_returns_prices_for_tickers(mock_get_current_prices, client):
    mock_get_current_prices.return_value = {'AAPL': 105.5, 'GOOG': 250.25}
    response = client.get('/api/prices?tickers=aapl,goog')
    assert response.status_code == 200
    assert response.json == {'prices': {'AAPL': 105.5, 'GOOG': 250.25}, 'not_found': []}
    mock_get_current_prices.assert_called_once_with(['AAPL', 'GOOG'])


@patch('routes.prices.price_service.get_current_prices')
def test_get_current_prices_lists_unresolved_tickers(mock_get_current_prices, client):
    mock_get_current_prices.return_value = {'AAPL': 105.5}
    response = client.get('/api/prices?tickers=AAPL,BADTICKER')
    assert response.status_code == 200
    assert response.json == {'prices': {'AAPL': 105.5}, 'not_found': ['BADTICKER']}


@patch('routes.prices.price_service.get_current_prices')
def test_get_current_prices_returns_404_when_none_resolve(mock_get_current_prices, client):
    mock_get_current_prices.return_value = {}
    response = client.get('/api/prices?tickers=BADTICKER')
    assert response.status_code == 404


def test_get_current_prices_requires_tickers_param(client):
    response = client.get('/api/prices')
    assert response.status_code == 400


@patch('routes.prices.price_service.get_current_prices')
def test_get_current_prices_returns_502_on_failure(mock_get_current_prices, client):
    mock_get_current_prices.side_effect = ConnectionError('Failed to connect to Yahoo Finance')
    response = client.get('/api/prices?tickers=AAPL')
    assert response.status_code == 502


def test_get_price_on_date_requires_date_param(client):
    response = client.get('/api/prices/AAPL')
    assert response.status_code == 400


def test_get_price_on_date_rejects_invalid_date_format(client):
    response = client.get('/api/prices/AAPL?date=not-a-date')
    assert response.status_code == 400


@patch('routes.prices.price_service.get_price_on_date')
def test_get_price_on_date_returns_price(mock_get_price_on_date, client):
    mock_get_price_on_date.return_value = 99.0
    response = client.get('/api/prices/AAPL?date=2026-07-20')
    assert response.status_code == 200
    assert response.json == {'ticker': 'AAPL', 'date': '2026-07-20', 'price': 99.0}


@patch('routes.prices.price_service.get_price_on_date')
def test_get_price_on_date_returns_404_when_not_found(mock_get_price_on_date, client):
    mock_get_price_on_date.side_effect = PriceNotFoundError("No price data found for 'AAPL' on 2026-07-20")
    response = client.get('/api/prices/AAPL?date=2026-07-20')
    assert response.status_code == 404


@patch('routes.prices.price_service.get_price_on_date')
def test_get_price_on_date_returns_502_on_unexpected_error(mock_get_price_on_date, client):
    mock_get_price_on_date.side_effect = ConnectionError('Failed to connect to Yahoo Finance')
    response = client.get('/api/prices/AAPL?date=2026-07-20')
    assert response.status_code == 502
