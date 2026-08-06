from typing import Optional

from pydantic import BaseModel

from models.AllocationSliceDTO import AllocationSliceDTO
from models.PortfolioHighlightDTO import PortfolioHighlightDTO
from models.PortfolioItemResultDTO import PortfolioItemResultDTO


class PortfolioResultDTO(BaseModel):
    """Response body for GET /api/portfolio: every holding plus portfolio-wide totals."""
    items: list[PortfolioItemResultDTO]
    totalValue: float
    totalCashBalance: float
    totalReturn: float
    totalReturnPercent: float
    # allocation breakdown by asset type (CASH included as its own slice), largest first
    allocationByType: list[AllocationSliceDTO] = []
    # portfolio-wide extremes among non-CASH holdings; None when there are none to highlight
    largestPosition: Optional[PortfolioHighlightDTO] = None
    topEarnerByAmount: Optional[PortfolioHighlightDTO] = None
    topEarnerByPercent: Optional[PortfolioHighlightDTO] = None
    worstEarnerByAmount: Optional[PortfolioHighlightDTO] = None
    worstEarnerByPercent: Optional[PortfolioHighlightDTO] = None
