from flask import Blueprint

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolio')


@portfolio_bp.route('', methods=['GET'])
def get_portfolio() -> tuple[dict, int]:
    return {'error': 'Portfolio endpoint - not implemented yet'}, 501


@portfolio_bp.route('/items', methods=['GET'])
def get_portfolio_items() -> tuple[dict, int]:
    return {'error': 'Portfolio items endpoint - not implemented yet'}, 501
