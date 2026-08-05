from pydantic import BaseModel

from models.PortfolioItemResultDTO import PortfolioItemResultDTO


class PortfolioResultDTO(BaseModel):
    """Response body for GET /api/portfolio: every holding plus portfolio-wide totals."""
    items: list[PortfolioItemResultDTO]
    totalValue: float
    totalCashBalance: float
    totalReturn: float
    totalReturnPercent: float
