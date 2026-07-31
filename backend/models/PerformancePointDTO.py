from pydantic import BaseModel


class PerformancePointDTO(BaseModel):
    """One chart point in a portfolio value history range."""
    date: str
    value: float
