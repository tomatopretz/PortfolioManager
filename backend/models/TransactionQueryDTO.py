from typing import Optional

from pydantic import BaseModel


class TransactionQueryDTO(BaseModel):
    """Query params for GET /api/transactions. Hidden from the Schemas panel via
    api.hide_from_schemas() — it's a filter, not a request/response DTO."""
    tickers: Optional[str] = None  # comma-separated ticker symbols, e.g. "AAPL,GOOG"
