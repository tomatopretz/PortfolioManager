from typing import Dict, List

from pydantic import BaseModel

from models.PerformancePointDTO import PerformancePointDTO


class PerformanceHistoryResultDTO(BaseModel):
    """Chart-ready portfolio value history for all supported frontend ranges."""
    ranges: Dict[str, List[PerformancePointDTO]]
