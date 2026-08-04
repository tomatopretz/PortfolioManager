import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app
from models.PortfolioItemDTO import PortfolioItemDTO
from models.PortfolioItemResultDTO import PortfolioItemResultDTO


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# --- GET /api/portfolio ------------------------------------------------------------------------

@patch('routes.portfolio.PortfolioService.get_enriched_portfolio')
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


@patch('routes.portfolio.PortfolioService.get_enriched_portfolio')
def test_get_portfolio_returns_empty_list(mock_get_portfolio, client):
    mock_get_portfolio.return_value = []
    response = client.get('/api/portfolio')
    assert response.status_code == 200
    assert response.json == []


@patch('routes.portfolio.PortfolioService.get_enriched_portfolio')
def test_get_portfolio_returns_502_on_failure(mock_get_portfolio, client):
    mock_get_portfolio.side_effect = ConnectionError('DB unreachable')
    response = client.get('/api/portfolio')
    assert response.status_code == 502


def test_portfolio_does_not_accept_post(client):
    # PortfolioItem is a derived view of transaction history - it's never created directly.
    # See POST /api/transactions for recording the buy/sell/deposit/withdraw that produces one.
    response = client.post('/api/portfolio', json={})
    assert response.status_code == 405


# --- GET /api/portfolio/<ticker>/<assetType> -----------------------------------------------------

def _result_item(**overrides):
    defaults = dict(
        id='1', ticker='AAPL', assetType='STOCK', quantity=10, costBasis=1000,
        currentPrice=150, marketValue=1500, unrealizedPnL=500,
    )
    defaults.update(overrides)
    return PortfolioItemResultDTO(**defaults)


@patch('routes.portfolio.PortfolioService.get_enriched_portfolio_item')
def test_get_portfolio_item_returns_item(mock_get_portfolio_item, client):
    mock_get_portfolio_item.return_value = _result_item()
    response = client.get('/api/portfolio/AAPL/STOCK')
    assert response.status_code == 200
    assert response.json['ticker'] == 'AAPL'
    mock_get_portfolio_item.assert_called_once_with('AAPL', 'STOCK')


@patch('routes.portfolio.PortfolioService.get_enriched_portfolio_item')
def test_get_portfolio_item_returns_404_when_not_found(mock_get_portfolio_item, client):
    mock_get_portfolio_item.return_value = None
    response = client.get('/api/portfolio/AAPL/STOCK')
    assert response.status_code == 404
    assert 'AAPL' in response.json['error']


@patch('routes.portfolio.PortfolioService.get_enriched_portfolio_item')
def test_get_portfolio_item_returns_502_on_failure(mock_get_portfolio_item, client):
    mock_get_portfolio_item.side_effect = ConnectionError('DB unreachable')
    response = client.get('/api/portfolio/AAPL/STOCK')
    assert response.status_code == 502


# --- PATCH /api/portfolio/<ticker>/<assetType>/favourite -----------------------------------------
# No price enrichment for a boolean flag toggle, so the response is a plain PortfolioItemDTO,
# not the enriched PortfolioItemResultDTO.

def _plain_item(**overrides):
    defaults = dict(id='1', ticker='AAPL', assetType='STOCK', quantity=10, costBasis=1000)
    defaults.update(overrides)
    return PortfolioItemDTO(**defaults)


@patch('routes.portfolio.PortfolioService.toggle_favourite')
def test_toggle_favourite_returns_updated_item(mock_toggle_favourite, client):
    mock_toggle_favourite.return_value = _plain_item(isFavourite=True)
    response = client.patch('/api/portfolio/AAPL/STOCK/favourite')
    assert response.status_code == 200
    assert response.json['isFavourite'] is True
    mock_toggle_favourite.assert_called_once_with('AAPL', 'STOCK')


@patch('routes.portfolio.PortfolioService.toggle_favourite')
def test_toggle_favourite_returns_404_when_not_found(mock_toggle_favourite, client):
    mock_toggle_favourite.return_value = None
    response = client.patch('/api/portfolio/AAPL/STOCK/favourite')
    assert response.status_code == 404


@patch('routes.portfolio.PortfolioService.toggle_favourite')
def test_toggle_favourite_returns_502_on_failure(mock_toggle_favourite, client):
    mock_toggle_favourite.side_effect = ConnectionError('DB unreachable')
    response = client.patch('/api/portfolio/AAPL/STOCK/favourite')
    assert response.status_code == 502
