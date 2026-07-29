from typing import Optional

from pydantic import BaseModel


class SingleTickerDateRequestDTO(BaseModel):
    """Query params for GET /api/prices/<ticker> (the ticker itself is a path param, not here).
    Hidden from the Schemas panel via api.hide_from_schemas() — date format is still validated
    manually in the route, this only exists so Swagger documents the param."""
    date: Optional[str] = None
