from flask import Blueprint
from flask_pydantic_spec import Response

from models.requests import TransactionRequest
from models.responses import ErrorResponse
from openapi import api

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolio')


# GET /api/portfolio - list all portfolio holdings
@portfolio_bp.route('', methods=['GET'])
@api.validate(resp=Response(HTTP_501=ErrorResponse), tags=['Portfolio'])
def get_portfolio() -> tuple[dict, int]:
    """Get all portfolio holdings."""
    return {'error': 'Portfolio endpoint - not implemented yet'}, 501


# POST /api/portfolio - record a buy or sell (`type` in the body picks the flow)
@portfolio_bp.route('', methods=['POST'])
@api.validate(body=TransactionRequest, resp=Response(HTTP_501=ErrorResponse), tags=['Portfolio'])
def record_transaction() -> tuple[dict, int]:
    """Record a buy or sell (`type` in the body picks the flow)."""
    return {'error': 'Portfolio transaction endpoint - not implemented yet'}, 501
