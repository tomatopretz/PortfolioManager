import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app
from models.PortfolioItemResultDTO import PortfolioItemResultDTO


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


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


def test_portfolio_does_not_accept_post(client):
    # PortfolioItem is a derived view of transaction history - it's never created directly.
    # See POST /api/transactions for recording the buy/sell/deposit/withdraw that produces one.
    response = client.post('/api/portfolio', json={})
    assert response.status_code == 405
