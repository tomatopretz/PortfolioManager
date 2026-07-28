from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Transaction(BaseModel):
    id: Optional[str] = None
    portfolioItemId: str  # tracks which portfolio item was affected
    type: str  # 'buy' or 'sell'
    quantity: float
    price: float
    date: datetime
    useCash: bool = True  # whether cash was used (true for sell, true/false for buy)
    # ticker and assetType come from the related PortfolioItem
