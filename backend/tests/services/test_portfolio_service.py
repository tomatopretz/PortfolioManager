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
    mock_list_items.return_value = [_item('CASH', quantity=500, cost_basis=500, asset_type='cash')]
    mock_list_prices.return_value = {}

    [result] = PortfolioService.get_portfolio()
    assert result.currentPrice is None
    assert result.marketValue is None
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
