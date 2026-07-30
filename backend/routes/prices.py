import logging
from datetime import datetime

from flask import Blueprint, request
from flask_pydantic_spec import Response

from models.ErrorResultDTO import ErrorResultDTO
from models.MultiTickerPriceResultDTO import MultiTickerPriceResultDTO
from models.MultiTickerPricesRequestDTO import MultiTickerPricesRequestDTO
from models.SingleTickerDatePriceResultDTO import SingleTickerDatePriceResultDTO
from models.SingleTickerDateRequestDTO import SingleTickerDateRequestDTO
from openapi import api
from services import price_service
from services.price_service import PriceNotFoundError

logger = logging.getLogger(__name__)

prices_bp = Blueprint('prices', __name__, url_prefix='/api/prices')

DATE_FORMAT = '%Y-%m-%d'  # strptime directive, for parsing
DATE_FORMAT_DISPLAY = 'YYYY-MM-DD'  # human-readable, for error messages

# query models still drive param validation + the Swagger Parameters list, just not the Schemas panel
api.hide_from_schemas(MultiTickerPricesRequestDTO, SingleTickerDateRequestDTO)


# GET /api/prices?tickers=AAPL,GOOG - current price for one or more tickers
@prices_bp.route('', methods=['GET'])
@api.validate(
    query=MultiTickerPricesRequestDTO,
    resp=Response(HTTP_200=MultiTickerPriceResultDTO, HTTP_404=ErrorResultDTO, HTTP_502=ErrorResultDTO),
    tags=['Prices'],
)
def get_current_prices() -> tuple[dict, int]:
    """Get current prices for one or more tickers, specified as a comma-separated list in the `tickers` query param."""
    tickers = price_service.parse_tickers(request.context.query.tickers)

    try:
        prices = price_service.list_current_prices(tickers)
    except Exception as e:
        logger.exception('Failed to fetch prices for tickers=%s', tickers)
        return {'error': f'Failed to fetch price data: {e}'}, 502

    if not prices:
        return {'error': f"No price data found for: {', '.join(tickers)}"}, 404
    not_found = [t for t in tickers if t not in prices]  # tickers yfinance couldn't resolve
    return {'prices': prices, 'not_found': not_found}, 200


# GET /api/prices/<ticker> - current price for a ticker, or its price on a date via ?date=YYYY-MM-DD
@prices_bp.route('/<ticker>', methods=['GET'])
@api.validate(
    query=SingleTickerDateRequestDTO,
    resp=Response(HTTP_200=SingleTickerDatePriceResultDTO, HTTP_422=ErrorResultDTO, HTTP_404=ErrorResultDTO, HTTP_502=ErrorResultDTO),
    tags=['Prices'],
)
def get_ticker_price(ticker: str) -> tuple[dict, int]:
    """Get the current price for one ticker, optionally filtering it to a specific date if `date` is given."""
    ticker = ticker.upper()
    date_str = request.context.query.date

    parsed_date = None
    if date_str is not None:
        try:
            parsed_date = datetime.strptime(date_str, DATE_FORMAT)
        except ValueError:
            return {'error': f'date must be in {DATE_FORMAT_DISPLAY} format'}, 422

    try:
        price = price_service.get_ticker_price(ticker, parsed_date)
    except PriceNotFoundError as e:
        return {'error': str(e)}, 404
    except Exception as e:
        logger.exception('Failed to fetch price for ticker=%s date=%s', ticker, date_str)
        return {'error': f'Failed to fetch price data: {e}'}, 502

    return {'ticker': ticker, 'date': date_str, 'price': price}, 200
