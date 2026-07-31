import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.PortfolioItemResultDTO import PortfolioItemResultDTO
from services.performance_service import PerformanceService


def _holding(
    ticker,
    asset_type='stock',
    quantity=10,
    cost_basis=1000,
    current_price=150,
    market_value=1500,
    unrealized_pnl=500,
):
    return PortfolioItemResultDTO(
        id='1',
        ticker=ticker,
        assetType=asset_type,
        quantity=quantity,
        costBasis=cost_basis,
        currentPrice=current_price,
        marketValue=market_value,
        unrealizedPnL=unrealized_pnl,
    )


@patch('services.performance_service._list_priced_holdings')
def test_get_performance_returns_zero_summary_for_empty_portfolio(mock_get_portfolio):
    mock_get_portfolio.return_value = []

    result = PerformanceService.get_performance()

    assert result.totalValue == 0.0
    assert result.totalCostBasis == 0.0
    assert result.totalPnL == 0.0
    assert result.totalPnLPercent == 0.0
    assert result.cashBalance == 0.0
    assert result.allocation == []


@patch('services.performance_service._list_priced_holdings')
def test_get_performance_includes_cash_balance_and_allocation(mock_get_portfolio):
    mock_get_portfolio.return_value = [
        _holding(
            'CASH',
            asset_type='cash',
            quantity=500,
            cost_basis=500,
            current_price=None,
            market_value=None,
            unrealized_pnl=None,
        )
    ]

    result = PerformanceService.get_performance()

    assert result.totalValue == 500.0
    assert result.totalCostBasis == 0.0
    assert result.totalPnL == 0.0
    assert result.totalPnLPercent == 0.0
    assert result.cashBalance == 500.0
    assert result.allocation[0].assetType == 'cash'
    assert result.allocation[0].value == 500.0
    assert result.allocation[0].percent == 100.0


@patch('services.performance_service._list_priced_holdings')
def test_get_performance_computes_stock_totals(mock_get_portfolio):
    mock_get_portfolio.return_value = [_holding('AAPL')]

    result = PerformanceService.get_performance()

    assert result.totalValue == 1500.0
    assert result.totalCostBasis == 1000.0
    assert result.totalPnL == 500.0
    assert result.totalPnLPercent == 50.0
    assert result.cashBalance == 0.0
    assert result.allocation[0].assetType == 'stock'
    assert result.allocation[0].value == 1500.0
    assert result.allocation[0].percent == 100.0


@patch('services.performance_service._list_priced_holdings')
def test_get_performance_groups_allocation_by_asset_type(mock_get_portfolio):
    mock_get_portfolio.return_value = [
        _holding('AAPL', asset_type='stock', market_value=1500, cost_basis=1000, unrealized_pnl=500),
        _holding('BND', asset_type='bond', market_value=500, cost_basis=600, unrealized_pnl=-100),
    ]

    result = PerformanceService.get_performance()

    allocation = {item.assetType: item for item in result.allocation}
    assert result.totalValue == 2000.0
    assert result.totalCostBasis == 1600.0
    assert result.totalPnL == 400.0
    assert result.totalPnLPercent == 25.0
    assert allocation['bond'].value == 500.0
    assert allocation['bond'].percent == 25.0
    assert allocation['stock'].value == 1500.0
    assert allocation['stock'].percent == 75.0


@patch('services.performance_service._list_priced_holdings')
def test_get_performance_excludes_holdings_without_price_from_totals(mock_get_portfolio):
    mock_get_portfolio.return_value = [
        _holding('AAPL'),
        _holding(
            'BADTICKER',
            market_value=None,
            unrealized_pnl=None,
            current_price=None,
        ),
    ]

    result = PerformanceService.get_performance()

    assert result.totalValue == 1500.0
    assert result.totalCostBasis == 1000.0
    assert result.totalPnL == 500.0
    assert len(result.allocation) == 1


@patch('services.performance_service._list_priced_holdings')
def test_get_performance_avoids_divide_by_zero_for_zero_cost_basis(mock_get_portfolio):
    mock_get_portfolio.return_value = [
        _holding('AAPL', cost_basis=0, market_value=1500, unrealized_pnl=1500)
    ]

    result = PerformanceService.get_performance()

    assert result.totalValue == 1500.0
    assert result.totalCostBasis == 0.0
    assert result.totalPnL == 1500.0
    assert result.totalPnLPercent == 0.0
