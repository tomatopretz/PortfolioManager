from pydantic import BaseModel


class MultiTickerPricesRequestDTO(BaseModel):
    """Query params for GET /api/prices (batch lookup across several tickers). Hidden from the
    Schemas panel via api.hide_from_schemas() — it's a filter, not a request/response DTO."""
    tickers: str  # comma-separated ticker symbols, e.g. "AAPL,GOOG"
