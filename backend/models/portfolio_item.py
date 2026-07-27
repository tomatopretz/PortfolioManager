from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PortfolioItem(BaseModel):
    id: Optional[str] = None
    ticker: str
    assetType: str  # 'stock', 'bond', etc
    quantity: float
    costBasis: float  # total cost of shares held
    lastUpdated: Optional[datetime] = None
