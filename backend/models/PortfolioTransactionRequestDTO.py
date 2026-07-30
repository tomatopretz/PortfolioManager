from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

CASH_TICKER = 'CASH'


class PortfolioTransactionRequestDTO(BaseModel):
    """Body for POST /api/portfolio. `type` picks buy (add-asset) vs sell (remove-asset)."""
    type: Literal['buy', 'sell']
    ticker: str
    assetType: str
    quantity: float = Field(gt=0)
    price: Optional[float] = Field(default=None, gt=0)  # not required for CASH operations
    useCash: bool = True  # only relevant when type == 'buy'; ignored for sells and CASH

    @field_validator('ticker')
    @classmethod
    def _normalize_ticker(cls, v: str) -> str:
        return v.strip().upper()

    @model_validator(mode='after')
    def _require_price_unless_cash(self) -> 'PortfolioTransactionRequestDTO':
        if self.ticker != CASH_TICKER and self.price is None:
            raise ValueError('price is required when ticker is not CASH')
        return self
