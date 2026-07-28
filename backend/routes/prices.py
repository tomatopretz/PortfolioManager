import logging
from datetime import datetime

from flask import Blueprint, request

from services import price_service
from services.price_service import PriceNotFoundError

logger = logging.getLogger(__name__)

prices_bp = Blueprint('prices', __name__, url_prefix='/api/prices')

# GET /api/prices?tickers=AAPL,GOOG - current price for one or more tickers
@prices_bp.route('', methods=['GET'])
def get_current_prices() -> tuple[dict, int]:
    tickers = price_service.parse_tickers(request.args.get('tickers', ''))
    if not tickers:
        return {'error': "Missing required query param 'tickers'"}, 400

    try:
        prices = price_service.get_current_prices(tickers)
    except Exception as e:
        logger.exception('Failed to fetch prices for tickers=%s', tickers)
        return {'error': f'Failed to fetch price data: {e}'}, 502

    if not prices:
        return {'error': f"No price data found for: {', '.join(tickers)}"}, 404
    not_found = [t for t in tickers if t not in prices]  # tickers yfinance couldn't resolve
    return {'prices': prices, 'not_found': not_found}, 200


# GET /api/prices/<ticker>?date=YYYY-MM-DD - historical price for one ticker on a specific date
@prices_bp.route('/<ticker>', methods=['GET'])
def get_price_on_date(ticker: str) -> tuple[dict, int]:
    date_param = request.args.get('date')
    if not date_param:
        return {'error': "Missing required query param 'date'. For current price use /api/prices?tickers="}, 400

    try:
        date = datetime.strptime(date_param, '%Y-%m-%d')
    except ValueError:
        return {'error': "Invalid 'date' format, expected YYYY-MM-DD"}, 400

    try:
        price = price_service.get_price_on_date(ticker, date)
    except PriceNotFoundError as e:
        return {'error': str(e)}, 404
    except Exception as e:
        logger.exception('Failed to fetch price for ticker=%s date=%s', ticker, date_param)
        return {'error': f'Failed to fetch price data: {e}'}, 502

    return {'ticker': ticker.upper(), 'date': date_param, 'price': price}, 200
