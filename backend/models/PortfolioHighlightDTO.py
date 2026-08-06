from typing import Optional

from pydantic import BaseModel


class PortfolioHighlightDTO(BaseModel):
    """A single non-CASH holding called out as a portfolio-wide extreme (largest position,
    top/worst earner by $ or %)."""
    ticker: str
    marketValue: Optional[float] = None
    pnl: Optional[float] = None
    gainLossPercent: Optional[float] = None
