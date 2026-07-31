from collections import defaultdict

from models.PerformanceAllocationDTO import PerformanceAllocationDTO
from models.PerformanceSummaryResultDTO import PerformanceSummaryResultDTO

CASH_TICKER = 'CASH'


def _list_priced_holdings():
    from services.portfolio_service import PortfolioService
    return PortfolioService.get_portfolio()


class PerformanceService:
    """Business logic for portfolio-level performance summary metrics."""

    @staticmethod
    def get_performance() -> PerformanceSummaryResultDTO:
        """Compute current aggregate performance from priced portfolio holdings."""
        holdings = _list_priced_holdings()

        total_value = 0.0
        total_cost_basis = 0.0
        total_pnl = 0.0
        cash_balance = 0.0
        allocation_values = defaultdict(float)

        for holding in holdings:
            if holding.ticker == CASH_TICKER:
                cash_value = round(holding.quantity, 2)
                cash_balance += cash_value
                total_value += cash_value
                allocation_values[holding.assetType] += cash_value
                continue

            if holding.marketValue is None or holding.unrealizedPnL is None:
                continue

            market_value = round(holding.marketValue, 2)
            cost_basis = round(holding.costBasis, 2)
            pnl = round(holding.unrealizedPnL, 2)

            total_value += market_value
            total_cost_basis += cost_basis
            total_pnl += pnl
            allocation_values[holding.assetType] += market_value

        total_value = round(total_value, 2)
        total_cost_basis = round(total_cost_basis, 2)
        total_pnl = round(total_pnl, 2)
        cash_balance = round(cash_balance, 2)
        total_pnl_percent = (
            round((total_pnl / total_cost_basis) * 100, 2)
            if total_cost_basis > 0
            else 0.0
        )

        allocation = [
            PerformanceAllocationDTO(
                assetType=asset_type,
                value=round(value, 2),
                percent=round((value / total_value) * 100, 2) if total_value > 0 else 0.0,
            )
            for asset_type, value in sorted(allocation_values.items())
            if value > 0
        ]

        return PerformanceSummaryResultDTO(
            totalValue=total_value,
            totalCostBasis=total_cost_basis,
            totalPnL=total_pnl,
            totalPnLPercent=total_pnl_percent,
            cashBalance=cash_balance,
            allocation=allocation,
        )
