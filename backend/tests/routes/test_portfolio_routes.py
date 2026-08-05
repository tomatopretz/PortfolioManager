import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app
from models.PortfolioItemDTO import PortfolioItemDTO
from models.PortfolioItemResultDTO import PortfolioItemResultDTO
from models.PortfolioResultDTO import PortfolioResultDTO


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# --- GET /api/portfolio ------------------------------------------------------------------------

@patch('routes.portfolio.PortfolioService.get_enriched_portfolio')  # mock: replace the service so no real DB/pricing call runs
def test_get_portfolio_returns_items(mock_get_portfolio, client):
    # Given the service returns one enriched item plus totals
    mock_get_portfolio.return_value = PortfolioResultDTO(
        items=[
            PortfolioItemResultDTO(
                id='1', ticker='AAPL', assetType='STOCK', quantity=10, costBasis=1000,
                currentPrice=150, marketValue=1500, pnl=500, gainLossPercent=50,
            ),
        ],
        totalValue=1500, totalCashBalance=0, totalReturn=500, totalReturnPercent=50,
    )
    # When calling GET /api/portfolio
    response = client.get('/api/portfolio')
    # Then the route returns 200 with that item and the portfolio totals serialized as JSON
    assert response.status_code == 200
    [item] = response.json['items']
    assert item['ticker'] == 'AAPL'
    assert item['marketValue'] == 1500
    assert response.json['totalValue'] == 1500
    assert response.json['totalReturn'] == 500
    assert response.json['totalReturnPercent'] == 50


@patch('routes.portfolio.PortfolioService.get_enriched_portfolio')  # mock: replace the service so no real DB/pricing call runs
def test_get_portfolio_returns_empty_list(mock_get_portfolio, client):
    # Given the service returns no items
    mock_get_portfolio.return_value = PortfolioResultDTO(
        items=[], totalValue=0, totalCashBalance=0, totalReturn=0, totalReturnPercent=0,
    )
    # When/Then calling GET /api/portfolio returns 200 with an empty items list, not an error
    response = client.get('/api/portfolio')
    assert response.status_code == 200
    assert response.json['items'] == []


@patch('routes.portfolio.PortfolioService.get_enriched_portfolio')  # mock: replace the service so no real DB/pricing call runs
def test_get_portfolio_returns_502_on_failure(mock_get_portfolio, client):
    # Given the service raises an error
    mock_get_portfolio.side_effect = ConnectionError('DB unreachable')
    # When/Then calling GET /api/portfolio translates the error into a 502 response
    response = client.get('/api/portfolio')
    assert response.status_code == 502



# --- GET /api/portfolio/<ticker>/<assetType> -----------------------------------------------------

def _result_item(**overrides):
    defaults = dict(
        id='1', ticker='AAPL', assetType='STOCK', quantity=10, costBasis=1000,
        currentPrice=150, marketValue=1500, pnl=500, gainLossPercent=50,
    )
    defaults.update(overrides)
    return PortfolioItemResultDTO(**defaults)


@patch('routes.portfolio.PortfolioService.get_enriched_portfolio_item')  # mock: replace the service so no real DB/pricing call runs
def test_get_portfolio_item_returns_item(mock_get_portfolio_item, client):
    # Given the service finds the item
    mock_get_portfolio_item.return_value = _result_item()
    # When calling GET /api/portfolio/AAPL/STOCK
    response = client.get('/api/portfolio/AAPL/STOCK')
    # Then the route returns 200 with that item, having passed the path params straight through
    assert response.status_code == 200
    assert response.json['ticker'] == 'AAPL'
    mock_get_portfolio_item.assert_called_once_with('AAPL', 'STOCK')


@patch('routes.portfolio.PortfolioService.get_enriched_portfolio_item')  # mock: replace the service so no real DB/pricing call runs
def test_get_portfolio_item_returns_404_when_not_found(mock_get_portfolio_item, client):
    # Given the service finds no matching item
    mock_get_portfolio_item.return_value = None
    # When/Then calling GET /api/portfolio/AAPL/STOCK returns 404 mentioning the ticker
    response = client.get('/api/portfolio/AAPL/STOCK')
    assert response.status_code == 404
    assert 'AAPL' in response.json['error']


@patch('routes.portfolio.PortfolioService.get_enriched_portfolio_item')  # mock: replace the service so no real DB/pricing call runs
def test_get_portfolio_item_returns_502_on_failure(mock_get_portfolio_item, client):
    # Given the service raises an error
    mock_get_portfolio_item.side_effect = ConnectionError('DB unreachable')
    # When/Then calling GET /api/portfolio/AAPL/STOCK translates the error into a 502 response
    response = client.get('/api/portfolio/AAPL/STOCK')
    assert response.status_code == 502


# --- PATCH /api/portfolio/<ticker>/<assetType>/favourite -----------------------------------------
# No price enrichment for a boolean flag toggle, so the response is a plain PortfolioItemDTO,
# not the enriched PortfolioItemResultDTO.

def _plain_item(**overrides):
    defaults = dict(id='1', ticker='AAPL', assetType='STOCK', quantity=10, costBasis=1000)
    defaults.update(overrides)
    return PortfolioItemDTO(**defaults)


@patch('routes.portfolio.PortfolioService.toggle_favourite')  # mock: replace the service so no real DB call runs
def test_toggle_favourite_returns_updated_item(mock_toggle_favourite, client):
    # Given the service flips isFavourite to True and returns the updated item
    mock_toggle_favourite.return_value = _plain_item(isFavourite=True)
    # When calling PATCH /api/portfolio/AAPL/STOCK/favourite (no body needed - it just toggles)
    response = client.patch('/api/portfolio/AAPL/STOCK/favourite')
    # Then the route returns 200 with the updated item
    assert response.status_code == 200
    assert response.json['isFavourite'] is True
    mock_toggle_favourite.assert_called_once_with('AAPL', 'STOCK')


@patch('routes.portfolio.PortfolioService.toggle_favourite')  # mock: replace the service so no real DB call runs
def test_toggle_favourite_returns_404_when_not_found(mock_toggle_favourite, client):
    # Given the service finds no matching item
    mock_toggle_favourite.return_value = None
    # When/Then calling PATCH .../favourite returns 404
    response = client.patch('/api/portfolio/AAPL/STOCK/favourite')
    assert response.status_code == 404


@patch('routes.portfolio.PortfolioService.toggle_favourite')  # mock: replace the service so no real DB call runs
def test_toggle_favourite_returns_502_on_failure(mock_toggle_favourite, client):
    # Given the service raises an error
    mock_toggle_favourite.side_effect = ConnectionError('DB unreachable')
    # When/Then calling PATCH .../favourite translates the error into a 502 response
    response = client.patch('/api/portfolio/AAPL/STOCK/favourite')
    assert response.status_code == 502
