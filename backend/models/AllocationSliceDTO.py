from pydantic import BaseModel


class AllocationSliceDTO(BaseModel):
    """One asset-type slice of the portfolio allocation breakdown."""
    assetType: str
    marketValue: float
    percent: float
