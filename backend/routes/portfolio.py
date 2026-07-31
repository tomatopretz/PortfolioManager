import logging

from flask import Blueprint, request
from flask_pydantic_spec import Response

from models.ErrorResultDTO import ErrorResultDTO
from models.PortfolioItemResultDTO import PortfolioItemResultDTO
from models.PortfolioTransactionRequestDTO import PortfolioTransactionRequestDTO
from models.TransactionDTO import TransactionDTO
from openapi import api
from services.portfolio_service import (
    InsufficientCashError,
    InsufficientQuantityError,
    PortfolioItemNotFoundError,
    PortfolioService,
)

logger = logging.getLogger(__name__)

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolio')


# GET /api/portfolio - list all portfolio holdings, with computed market value / unrealized P&L
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


# POST /api/portfolio - record a buy or sell (`type` in the body picks the flow)
@portfolio_bp.route('', methods=['POST'])
@api.validate(
    body=PortfolioTransactionRequestDTO,
    resp=Response(
        HTTP_201=TransactionDTO, HTTP_404=ErrorResultDTO, HTTP_422=ErrorResultDTO, HTTP_502=ErrorResultDTO,
        validate=False,
    ),
    tags=['Portfolio'],
)
def record_transaction() -> tuple[dict, int]:
    """Record a buy or sell (`type` in the body picks the flow: add/deposit vs remove/withdraw)."""
    transaction_request = request.context.body

    try:
        transaction = PortfolioService.record_transaction(transaction_request)
    except PortfolioItemNotFoundError as e:
        return {'error': str(e)}, 404
    except (InsufficientCashError, InsufficientQuantityError) as e:
        return {'error': str(e)}, 422
    except Exception as e:
        logger.exception('Failed to record portfolio transaction')
        return {'error': f'Failed to record portfolio transaction: {e}'}, 502

    return transaction.model_dump(), 201
