from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PortfolioItemDTO(BaseModel):
    id: Optional[str] = None
    ticker: str
    assetType: str  # 'stock', 'bond', etc
    quantity: float
    costBasis: float  # total cost of shares held
    lastUpdated: Optional[datetime] = None
