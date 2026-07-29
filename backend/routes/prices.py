import logging
from datetime import datetime

from flask import Blueprint, request
from flask_pydantic_spec import Response

from models.requests import DATE_FORMAT, DATE_FORMAT_DISPLAY, MultiTickerPricesRequest
from models.responses import ErrorResponse, MultiTickerPriceResponse, SingleTickerDatePriceResponse
from openapi import api
from services import price_service
from services.price_service import PriceNotFoundError

logger = logging.getLogger(__name__)

prices_bp = Blueprint('prices', __name__, url_prefix='/api/prices')

# query model still drives param validation + the Swagger Parameters list, just not the Schemas panel
api.hide_from_schemas(MultiTickerPricesRequest)


# GET /api/prices?tickers=AAPL,GOOG - current price for one or more tickers
@prices_bp.route('', methods=['GET'])
@api.validate(
    query=MultiTickerPricesRequest,
    resp=Response(HTTP_200=MultiTickerPriceResponse, HTTP_404=ErrorResponse, HTTP_502=ErrorResponse),
    tags=['Prices'],
)
def get_current_prices() -> tuple[dict, int]:
    """Get current prices for one or more tickers."""
    tickers = price_service.parse_tickers(request.context.query.tickers)

    try:
        prices = price_service.get_current_prices(tickers)
    except Exception as e:
        logger.exception('Failed to fetch prices for tickers=%s', tickers)
        return {'error': f'Failed to fetch price data: {e}'}, 502

    if not prices:
        return {'error': f"No price data found for: {', '.join(tickers)}"}, 404
    not_found = [t for t in tickers if t not in prices]  # tickers yfinance couldn't resolve
    return {'prices': prices, 'not_found': not_found}, 200


# GET /api/prices/<ticker>/<date> - historical price for exactly one ticker on exactly one date (YYYY-MM-DD)
@prices_bp.route('/<ticker>/<date>', methods=['GET'])
@api.validate(
    resp=Response(HTTP_200=SingleTickerDatePriceResponse, HTTP_422=ErrorResponse, HTTP_404=ErrorResponse, HTTP_502=ErrorResponse),
    tags=['Prices'],
)
def get_price_on_date(ticker: str, date: str) -> tuple[dict, int]:
    """Get the price for a ticker on a specific date."""
    ticker = ticker.upper()

    try:
        parsed_date = datetime.strptime(date, DATE_FORMAT)
    except ValueError:
        return {'error': f'date must be in {DATE_FORMAT_DISPLAY} format'}, 422

    try:
        price = price_service.get_price_on_date(ticker, parsed_date)
    except PriceNotFoundError as e:
        return {'error': str(e)}, 404
    except Exception as e:
        logger.exception('Failed to fetch price for ticker=%s date=%s', ticker, date)
        return {'error': f'Failed to fetch price data: {e}'}, 502

    return {'ticker': ticker, 'date': date, 'price': price}, 200
