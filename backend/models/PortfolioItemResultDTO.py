from typing import Optional

from pydantic import BaseModel


class PortfolioItemResultDTO(BaseModel):
    """One entry in the GET /api/portfolio items list."""
    id: str
    ticker: str
    assetType: str
    quantity: float
    costBasis: float
    lastUpdated: Optional[str] = None
    currentPrice: Optional[float] = None  # None if the ticker couldn't be priced
    marketValue: Optional[float] = None
    unrealizedPnL: Optional[float] = None
