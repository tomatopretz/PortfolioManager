from pydantic import BaseModel


class PerformanceAllocationDTO(BaseModel):
    """One asset allocation slice in the portfolio performance summary."""
    assetType: str
    value: float
    percent: float
