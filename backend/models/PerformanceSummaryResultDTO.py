from typing import List

from pydantic import BaseModel

from models.PerformanceAllocationDTO import PerformanceAllocationDTO


class PerformanceSummaryResultDTO(BaseModel):
    """Portfolio-level aggregate performance metrics."""
    totalValue: float
    totalCostBasis: float
    totalPnL: float
    totalPnLPercent: float
    cashBalance: float
    allocation: List[PerformanceAllocationDTO]
