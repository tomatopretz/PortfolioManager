import logging

from flask import Blueprint, Response as FlaskResponse, request
from flask_pydantic_spec import Response

from models.BulkRecordTransactionsRequestDTO import BulkRecordTransactionsRequestDTO
from models.BulkTransactionsResultDTO import BulkTransactionsResultDTO
from models.ErrorResultDTO import ErrorResultDTO
from models.RecordTransactionRequestDTO import RecordTransactionRequestDTO
from models.TransactionDTO import TransactionDTO
from models.TransactionQueryDTO import TransactionQueryDTO
from openapi import api
from services import price_service
from services.transaction_service import InsufficientBalanceError, PortfolioItemNotFoundError, TransactionService

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


# GET /api/transactions/export - CSV export generated from backend transaction history.
@transactions_bp.route('/export', methods=['GET'])
@api.validate(
    resp=Response(HTTP_200=None, HTTP_502=ErrorResultDTO, validate=False),
    tags=['Transactions'],
)
def export_transactions() -> tuple[FlaskResponse, int] | tuple[dict, int]:
    """Export transactions as CSV with ticker/type joined from portfolio items."""
    try:
        csv_body = TransactionService.export_transactions_csv()
    except Exception as e:
        logger.exception('Failed to export transactions')
        return {'error': f'Failed to export transactions: {e}'}, 502

    return FlaskResponse(
        csv_body,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=transactions.csv'},
    ), 200


# POST /api/transactions - record a buy/sell (`type` + `assetType` pick the flow: add/deposit vs
# remove/withdraw, stock/bond vs CASH). This is the only path that writes a Transaction - it
# always keeps the corresponding PortfolioItem's quantity/costBasis in sync as part of the same
# atomic operation.
@transactions_bp.route('', methods=['POST'])
@api.validate(
    body=RecordTransactionRequestDTO,
    resp=Response(
        HTTP_201=TransactionDTO, HTTP_404=ErrorResultDTO, HTTP_422=ErrorResultDTO, HTTP_502=ErrorResultDTO,
        validate=False,
    ),
    tags=['Transactions'],
)
def create_transaction() -> tuple[dict, int]:
    """Record a buy or sell (`type` in the body picks the flow: add/deposit vs remove/withdraw)."""
    transaction_request = request.context.body

    try:
        created = TransactionService.record_transaction(transaction_request)
    except PortfolioItemNotFoundError as e:
        return {'error': str(e)}, 404
    except InsufficientBalanceError as e:
        return {'error': str(e)}, 422
    except Exception as e:
        logger.exception('Failed to create transaction')
        return {'error': f'Failed to create transaction: {e}'}, 502

    return created.model_dump(), 201


# POST /api/transactions/bulk - record many transactions in one atomic operation. The existing
# single POST path remains separate so this import-only endpoint can be rolled back cleanly.
@transactions_bp.route('/bulk', methods=['POST'])
@api.validate(
    body=BulkRecordTransactionsRequestDTO,
    resp=Response(
        HTTP_201=BulkTransactionsResultDTO, HTTP_404=ErrorResultDTO, HTTP_422=ErrorResultDTO, HTTP_502=ErrorResultDTO,
        validate=False,
    ),
    tags=['Transactions'],
)
def create_transactions_bulk() -> tuple[dict, int]:
    """Record multiple transactions atomically."""
    bulk_request = request.context.body

    try:
        created = TransactionService.record_transactions_bulk(bulk_request.transactions)
    except PortfolioItemNotFoundError as e:
        return {'error': str(e)}, 404
    except InsufficientBalanceError as e:
        return {'error': str(e)}, 422
    except Exception as e:
        logger.exception('Failed to create transactions in bulk')
        return {'error': f'Failed to create transactions in bulk: {e}'}, 502

    return {
        'count': len(created),
        'created': [transaction.model_dump() for transaction in created],
    }, 201
