import logging

from flask import Blueprint
from flask_pydantic_spec import Response

from models.ErrorResultDTO import ErrorResultDTO
from models.PortfolioItemResultDTO import PortfolioItemResultDTO
from openapi import api
from services.portfolio_service import PortfolioService

logger = logging.getLogger(__name__)

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolio')


# GET /api/portfolio - list all portfolio holdings, with computed market value / unrealized P&L.
# Read-only: a PortfolioItem is a derived view of transaction history, never created directly -
# see POST /api/transactions for recording the buy/sell/deposit/withdraw that produces one.
@portfolio_bp.route('', methods=['GET'])
@api.validate(resp=Response(HTTP_200=list[PortfolioItemResultDTO], HTTP_502=ErrorResultDTO, validate=False), tags=['Portfolio'])
def get_portfolio() -> tuple[list[dict], int]:
    """Get all portfolio holdings."""
    try:
        items = PortfolioService.get_portfolio()
    except Exception as e:
        logger.exception('Failed to fetch portfolio')
        return {'error': f'Failed to fetch portfolio: {e}'}, 502

    return [item.model_dump() for item in items], 200


# GET /api/portfolio/<ticker>/<assetType> - get a single portfolio holding by its natural key
@portfolio_bp.route('/<ticker>/<asset_type>', methods=['GET'])
@api.validate(
    resp=Response(HTTP_200=PortfolioItemResultDTO, HTTP_404=ErrorResultDTO, HTTP_502=ErrorResultDTO, validate=False),
    tags=['Portfolio'],
)
def get_portfolio_item(ticker: str, asset_type: str) -> tuple[dict, int]:
    """Get a single portfolio holding by ticker + assetType."""
    try:
        item = PortfolioService.get_portfolio_item(ticker, asset_type)
    except Exception as e:
        logger.exception('Failed to fetch portfolio item ticker=%s assetType=%s', ticker, asset_type)
        return {'error': f'Failed to fetch portfolio item: {e}'}, 502

    if item is None:
        return {'error': f"No portfolio item found for ticker '{ticker.upper()}' ({asset_type.upper()})"}, 404

    return item.model_dump(), 200
