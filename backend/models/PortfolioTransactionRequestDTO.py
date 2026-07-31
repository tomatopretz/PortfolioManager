from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

CASH_TICKER = 'USD'  # no multi-currency support - USD is the one cash "ticker"
CASH_ASSET_TYPE = 'CASH'


class PortfolioTransactionRequestDTO(BaseModel):
    """Body for POST /api/portfolio. `type` picks buy (add-asset) vs sell (remove-asset)."""
    type: Literal['buy', 'sell']
    ticker: str
    assetType: str
    quantity: float = Field(gt=0)
    price: Optional[float] = Field(default=None, gt=0)  # not required for CASH operations
    useCash: bool = True  # only relevant when type == 'buy'; ignored for sells and CASH

    @field_validator('ticker', 'assetType')
    @classmethod
    def _normalize_upper(cls, v: str) -> str:
        return v.strip().upper()

    @model_validator(mode='after')
    def _require_price_unless_cash(self) -> 'PortfolioTransactionRequestDTO':
        if self.assetType != CASH_ASSET_TYPE and self.price is None:
            raise ValueError('price is required when assetType is not CASH')
        return self
