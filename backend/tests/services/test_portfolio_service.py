import os
import sys
from datetime import datetime, timezone
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.PortfolioItemDTO import PortfolioItemDTO
from services.portfolio_service import PortfolioService


def _item(ticker, quantity, cost_basis, asset_type='stock'):
    return PortfolioItemDTO(
        id='1', ticker=ticker, assetType=asset_type, quantity=quantity, costBasis=cost_basis,
        lastUpdated=datetime.now(timezone.utc),
    )


@patch('services.portfolio_service.PortfolioItemService.list_portfolio_items')
def test_get_portfolio_returns_empty_list_for_empty_portfolio(mock_list_items):
    mock_list_items.return_value = []
    assert PortfolioService.get_portfolio() == []


@patch('services.portfolio_service.price_service.list_current_prices')
@patch('services.portfolio_service.PortfolioItemService.list_portfolio_items')
def test_get_portfolio_computes_market_value_and_pnl(mock_list_items, mock_list_prices):
    mock_list_items.return_value = [_item('AAPL', quantity=10, cost_basis=1000)]
    mock_list_prices.return_value = {'AAPL': 150.0}

    [result] = PortfolioService.get_portfolio()
    assert result.currentPrice == 150.0
    assert result.marketValue == 1500.0
    assert result.unrealizedPnL == 500.0
    mock_list_prices.assert_called_once_with(['AAPL'])


@patch('services.portfolio_service.price_service.list_current_prices')
@patch('services.portfolio_service.PortfolioItemService.list_portfolio_items')
def test_get_portfolio_cash_has_no_price_or_pnl(mock_list_items, mock_list_prices):
    mock_list_items.return_value = [_item('USD', quantity=500, cost_basis=500, asset_type='CASH')]
    mock_list_prices.return_value = {}

    [result] = PortfolioService.get_portfolio()
    assert result.currentPrice is None
    assert result.marketValue == 500  # cash marketValue is just its quantity, always at par
    assert result.unrealizedPnL is None
    mock_list_prices.assert_not_called()  # no non-CASH tickers, so no price lookup needed at all


@patch('services.portfolio_service.price_service.list_current_prices')
@patch('services.portfolio_service.PortfolioItemService.list_portfolio_items')
def test_get_portfolio_flags_unresolvable_ticker_as_stale(mock_list_items, mock_list_prices):
    mock_list_items.return_value = [_item('BADTICKER', quantity=5, cost_basis=100)]
    mock_list_prices.return_value = {}

    [result] = PortfolioService.get_portfolio()
    assert result.currentPrice is None
    assert result.marketValue is None
    assert result.unrealizedPnL is None


@patch('services.portfolio_service.PortfolioItemService.get_portfolio_item_by_ticker_and_asset_type')
def test_get_portfolio_item_returns_none_when_not_found(mock_get_item):
    mock_get_item.return_value = None
    assert PortfolioService.get_portfolio_item('AAPL', 'STOCK') is None


@patch('services.portfolio_service.price_service.list_current_prices')
@patch('services.portfolio_service.PortfolioItemService.get_portfolio_item_by_ticker_and_asset_type')
def test_get_portfolio_item_computes_market_value_and_pnl(mock_get_item, mock_list_prices):
    mock_get_item.return_value = _item('AAPL', quantity=10, cost_basis=1000)
    mock_list_prices.return_value = {'AAPL': 150.0}

    result = PortfolioService.get_portfolio_item('AAPL', 'STOCK')
    assert result.currentPrice == 150.0
    assert result.marketValue == 1500.0
    assert result.unrealizedPnL == 500.0
    mock_list_prices.assert_called_once_with(['AAPL'])


@patch('services.portfolio_service.price_service.list_current_prices')
@patch('services.portfolio_service.PortfolioItemService.get_portfolio_item_by_ticker_and_asset_type')
def test_get_portfolio_item_cash_has_no_price_or_pnl(mock_get_item, mock_list_prices):
    mock_get_item.return_value = _item('USD', quantity=500, cost_basis=500, asset_type='CASH')

    result = PortfolioService.get_portfolio_item('USD', 'CASH')
    assert result.currentPrice is None
    assert result.marketValue == 500
    assert result.unrealizedPnL is None
    mock_list_prices.assert_not_called()  # CASH never needs a price lookup


@patch('services.portfolio_service.PortfolioItemService.toggle_favourite')
def test_toggle_favourite_returns_none_when_item_not_found(mock_toggle_favourite):
    mock_toggle_favourite.return_value = None
    assert PortfolioService.toggle_favourite('AAPL', 'STOCK') is None


@patch('services.portfolio_service.price_service.list_current_prices')
@patch('services.portfolio_service.PortfolioItemService.toggle_favourite')
def test_toggle_favourite_returns_enriched_item(mock_toggle_favourite, mock_list_prices):
    item = _item('AAPL', quantity=10, cost_basis=1000)
    item.isFavourite = True
    mock_toggle_favourite.return_value = item
    mock_list_prices.return_value = {'AAPL': 150.0}

    result = PortfolioService.toggle_favourite('aapl', 'stock')

    mock_toggle_favourite.assert_called_once_with('aapl', 'stock')
    assert result.isFavourite is True
    assert result.marketValue == 1500.0
