import logging
import uuid

from flask import Blueprint, request
from flask_pydantic_spec import Response
from psycopg.errors import ForeignKeyViolation

from models.ErrorResultDTO import ErrorResultDTO
from models.TransactionDTO import TransactionDTO
from models.TransactionQueryDTO import TransactionQueryDTO
from openapi import api
from services import price_service
from services.transaction_service import TransactionService

logger = logging.getLogger(__name__)

transactions_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

# query model still drives param validation + the Swagger Parameters list, just not the Schemas panel
api.hide_from_schemas(TransactionQueryDTO)


# GET /api/transactions?tickers=AAPL,GOOG - list all recorded transactions, optionally filtered by ticker(s)
@transactions_bp.route('', methods=['GET'])
@api.validate(
    query=TransactionQueryDTO,
    resp=Response(HTTP_200=list[TransactionDTO], HTTP_502=ErrorResultDTO, validate=False),
    tags=['Transactions'],
)
def get_transactions() -> tuple[list[dict], int]:
    """Get all recorded transactions, optionally filtered to one or more tickers."""
    tickers_param = request.context.query.tickers
    tickers = price_service.parse_tickers(tickers_param) if tickers_param else None

    try:
        transactions = TransactionService.list_transactions(tickers)
    except Exception as e:
        logger.exception('Failed to fetch transactions')
        return {'error': f'Failed to fetch transactions: {e}'}, 502

    return [transaction.model_dump() for transaction in transactions], 200


# POST /api/transactions - record a new transaction
@transactions_bp.route('', methods=['POST'])
@api.validate(
    body=TransactionDTO,
    resp=Response(HTTP_201=TransactionDTO, HTTP_404=ErrorResultDTO, HTTP_502=ErrorResultDTO, validate=False),
    tags=['Transactions'],
)
def create_transaction() -> tuple[dict, int]:
    """Record a new transaction."""
    transaction = request.context.body

    try:
        created = TransactionService.add_transaction(transaction)
    except ForeignKeyViolation:
        return {'error': f'No portfolio item found with id {transaction.portfolioItemId}'}, 404
    except Exception as e:
        logger.exception('Failed to create transaction')
        return {'error': f'Failed to create transaction: {e}'}, 502

    return created.model_dump(), 201


# DELETE /api/transactions/<transaction_id> - delete a transaction
@transactions_bp.route('/<transaction_id>', methods=['DELETE'])
@api.validate(resp=Response(HTTP_404=ErrorResultDTO, HTTP_422=ErrorResultDTO, HTTP_502=ErrorResultDTO), tags=['Transactions'])
def delete_transaction(transaction_id: str) -> tuple[str, int]:
    """Delete a transaction."""
    try:
        uuid.UUID(transaction_id)
    except ValueError:
        return {'error': f'transaction_id must be a valid UUID, got: {transaction_id}'}, 422

    try:
        deleted = TransactionService.delete_transaction(transaction_id)
    except Exception as e:
        logger.exception('Failed to delete transaction id=%s', transaction_id)
        return {'error': f'Failed to delete transaction: {e}'}, 502

    if not deleted:
        return {'error': f'No transaction found with id {transaction_id}'}, 404

    return '', 204
