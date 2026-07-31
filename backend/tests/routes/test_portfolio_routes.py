import os
import sys
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app
from models.PortfolioItemResultDTO import PortfolioItemResultDTO
from models.TransactionDTO import TransactionDTO
from services.portfolio_service import InsufficientCashError, InsufficientQuantityError, PortfolioItemNotFoundError


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def _transaction(**overrides):
    defaults = dict(
        id='11111111-1111-1111-1111-111111111111',
        portfolioItemId='22222222-2222-2222-2222-222222222222',
        type='buy', quantity=10, price=150, date=datetime(2026, 7, 31, tzinfo=timezone.utc), useCash=True,
    )
    defaults.update(overrides)
    return TransactionDTO(**defaults)


# --- GET /api/portfolio ------------------------------------------------------------------------

@patch('routes.portfolio.PortfolioService.get_portfolio')
def test_get_portfolio_returns_items(mock_get_portfolio, client):
    mock_get_portfolio.return_value = [
        PortfolioItemResultDTO(
            id='1', ticker='AAPL', assetType='STOCK', quantity=10, costBasis=1000,
            currentPrice=150, marketValue=1500, unrealizedPnL=500,
        ),
    ]
    response = client.get('/api/portfolio')
    assert response.status_code == 200
    [item] = response.json
    assert item['ticker'] == 'AAPL'
    assert item['marketValue'] == 1500


@patch('routes.portfolio.PortfolioService.get_portfolio')
def test_get_portfolio_returns_empty_list(mock_get_portfolio, client):
    mock_get_portfolio.return_value = []
    response = client.get('/api/portfolio')
    assert response.status_code == 200
    assert response.json == []


@patch('routes.portfolio.PortfolioService.get_portfolio')
def test_get_portfolio_returns_502_on_failure(mock_get_portfolio, client):
    mock_get_portfolio.side_effect = ConnectionError('DB unreachable')
    response = client.get('/api/portfolio')
    assert response.status_code == 502


# --- POST /api/portfolio -----------------------------------------------------------------------

def _buy_body(**overrides):
    body = dict(type='buy', ticker='AAPL', assetType='stock', quantity=10, price=150, useCash=True)
    body.update(overrides)
    return body


@patch('routes.portfolio.PortfolioService.record_transaction')
def test_record_transaction_returns_201_on_success(mock_record_transaction, client):
    mock_record_transaction.return_value = _transaction()
    response = client.post('/api/portfolio', json=_buy_body())
    assert response.status_code == 201
    assert response.json['type'] == 'buy'
    assert response.json['quantity'] == 10


@patch('routes.portfolio.PortfolioService.record_transaction')
def test_record_transaction_normalizes_ticker_and_asset_type_case(mock_record_transaction, client):
    mock_record_transaction.return_value = _transaction()
    client.post('/api/portfolio', json=_buy_body(ticker='aapl', assetType='stock'))

    [sent_request], _ = mock_record_transaction.call_args
    assert sent_request.ticker == 'AAPL'
    assert sent_request.assetType == 'STOCK'


def test_record_transaction_rejects_missing_required_fields(client):
    response = client.post('/api/portfolio', json={'type': 'buy'})
    assert response.status_code == 422
    assert 'ticker' in response.json['error']


def test_record_transaction_rejects_missing_price_for_non_cash(client):
    response = client.post('/api/portfolio', json=_buy_body(price=None))
    assert response.status_code == 422


@patch('routes.portfolio.PortfolioService.record_transaction')
def test_record_transaction_returns_404_when_item_not_found(mock_record_transaction, client):
    mock_record_transaction.side_effect = PortfolioItemNotFoundError("No portfolio item found for ticker 'AAPL'")
    response = client.post('/api/portfolio', json=_buy_body(type='sell'))
    assert response.status_code == 404
    assert 'AAPL' in response.json['error']


@patch('routes.portfolio.PortfolioService.record_transaction')
def test_record_transaction_returns_422_on_insufficient_cash(mock_record_transaction, client):
    mock_record_transaction.side_effect = InsufficientCashError('CASH balance 100 is less than purchase cost 1500')
    response = client.post('/api/portfolio', json=_buy_body())
    assert response.status_code == 422


@patch('routes.portfolio.PortfolioService.record_transaction')
def test_record_transaction_returns_422_on_insufficient_quantity(mock_record_transaction, client):
    mock_record_transaction.side_effect = InsufficientQuantityError("Cannot sell 100 of 'AAPL': only 5 held")
    response = client.post('/api/portfolio', json=_buy_body(type='sell'))
    assert response.status_code == 422


@patch('routes.portfolio.PortfolioService.record_transaction')
def test_record_transaction_returns_502_on_unexpected_error(mock_record_transaction, client):
    mock_record_transaction.side_effect = ConnectionError('DB unreachable')
    response = client.post('/api/portfolio', json=_buy_body())
    assert response.status_code == 502
