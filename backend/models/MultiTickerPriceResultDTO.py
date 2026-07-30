from pydantic import BaseModel


class MultiTickerPriceResultDTO(BaseModel):
    """Response body for GET /api/prices (batch lookup across several tickers)."""
    prices: dict[str, float]
    not_found: list[str]
