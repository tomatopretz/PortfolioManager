from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str

class MultiTickerPriceResponse(BaseModel):
    """Response body for GET /api/prices (batch lookup across several tickers)."""
    prices: dict[str, float]
    not_found: list[str]

class SingleTickerDatePriceResponse(BaseModel):
    """Response body for GET /api/prices/<ticker>/<date>."""
    ticker: str
    date: str
    price: float
