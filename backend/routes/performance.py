import logging
from typing import Dict, Tuple

from flask import Blueprint
from flask_pydantic_spec import Response

from models.ErrorResultDTO import ErrorResultDTO
from models.PerformanceSummaryResultDTO import PerformanceSummaryResultDTO
from openapi import api
from services.performance_service import PerformanceService

logger = logging.getLogger(__name__)

performance_bp = Blueprint('performance', __name__, url_prefix='/api/performance')


# GET /api/performance - portfolio-level performance summary metrics
@performance_bp.route('', methods=['GET'])
@api.validate(
    resp=Response(HTTP_200=PerformanceSummaryResultDTO, HTTP_502=ErrorResultDTO, validate=False),
    tags=['Performance'],
)
def get_performance() -> Tuple[Dict, int]:
    """Get aggregate portfolio performance metrics."""
    try:
        performance = PerformanceService.get_performance()
    except Exception as e:
        logger.exception('Failed to fetch performance')
        return {'error': f'Failed to fetch performance: {e}'}, 502

    return performance.model_dump(), 200
