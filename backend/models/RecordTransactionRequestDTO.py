from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

CASH_TICKER = 'USD'  # no multi-currency support - USD is the one cash "ticker"
CASH_ASSET_TYPE = 'CASH'


class RecordTransactionRequestDTO(BaseModel):
    """Body for POST /api/transactions. `type` picks buy (add-asset/deposit) vs sell
    (remove-asset/withdraw); `assetType` picks stock/bond vs CASH."""
    type: Literal['buy', 'sell']
    ticker: str
    assetType: str
    quantity: float = Field(gt=0)
    price: Optional[float] = Field(default=None, gt=0)  # not required for CASH operations
    useCash: bool = True  # only relevant when type == 'buy'; ignored for sells and CASH
    date: Optional[datetime] = None  # defaults to now() server-side if omitted; set to backdate a trade

    @field_validator('ticker', 'assetType')
    @classmethod
    def _normalize_upper(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator('date', mode='before')
    @classmethod
    def _parse_date(cls, v):
        if v is None or isinstance(v, datetime):
            return v
        try:
            return datetime.fromisoformat(str(v))
        except ValueError:
            raise ValueError(
                "date must be in ISO 8601 format, e.g. '2026-01-15T00:00:00Z' or '2026-01-15'"
            ) from None

    @field_validator('date')
    @classmethod
    def _ensure_timezone_aware(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    @model_validator(mode='after')
    def _require_price_unless_cash(self) -> 'RecordTransactionRequestDTO':
        if self.assetType != CASH_ASSET_TYPE and self.price is None:
            raise ValueError('price is required when assetType is not CASH')
        return self

    @model_validator(mode='after')
    def _require_consistent_cash_ticker(self) -> 'RecordTransactionRequestDTO':
        is_cash_asset_type = self.assetType == CASH_ASSET_TYPE
        is_cash_ticker = self.ticker == CASH_TICKER
        if is_cash_asset_type != is_cash_ticker:
            raise ValueError(
                f"ticker must be '{CASH_TICKER}' when assetType is '{CASH_ASSET_TYPE}', and vice versa"
            )
        return self
