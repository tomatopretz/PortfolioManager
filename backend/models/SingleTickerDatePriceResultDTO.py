from typing import Optional

from pydantic import BaseModel


class SingleTickerDatePriceResultDTO(BaseModel):
    """Response body for GET /api/prices/<ticker>."""
    ticker: str
    price: float
    date: Optional[str] = None  # present only when ?date= was given
