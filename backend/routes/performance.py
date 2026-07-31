import logging
from typing import Dict, Tuple

from flask import Blueprint
from flask_pydantic_spec import Response

from models.ErrorResultDTO import ErrorResultDTO
from models.PerformanceHistoryResultDTO import PerformanceHistoryResultDTO
from openapi import api
from services.performance_service import PerformanceService

logger = logging.getLogger(__name__)

performance_bp = Blueprint('performance', __name__, url_prefix='/api/performance')


# GET /api/performance - chart-ready portfolio value history for all supported ranges
@performance_bp.route('', methods=['GET'])
@api.validate(
    resp=Response(HTTP_200=PerformanceHistoryResultDTO, HTTP_502=ErrorResultDTO, validate=False),
    tags=['Performance'],
)
def get_performance() -> Tuple[Dict, int]:
    """Get chart-ready portfolio value history for 1D, 1W, 1M, 6M, 1Y, and ALL ranges."""
    try:
        performance = PerformanceService.get_performance()
    except Exception as e:
        logger.exception('Failed to fetch performance history')
        return {'error': f'Failed to fetch performance history: {e}'}, 502

    return performance.model_dump(), 200
