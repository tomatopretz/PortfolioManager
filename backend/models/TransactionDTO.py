import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class TransactionDTO(BaseModel):
    id: Optional[str] = None
    portfolioItemId: str  # tracks which portfolio item was affected
    type: Literal['buy', 'sell']
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)
    date: datetime
    useCash: bool = True  # whether cash was used (true for sell, true/false for buy)
    # ticker and assetType come from the related PortfolioItem

    @field_validator('portfolioItemId')
    @classmethod
    def _validate_portfolio_item_id(cls, v: str) -> str:
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError('portfolioItemId must be a valid UUID')
        return v
