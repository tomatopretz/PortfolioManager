from typing import Optional

from models.PortfolioItemDTO import PortfolioItemDTO
from models.PortfolioItemResultDTO import PortfolioItemResultDTO
from models.RecordTransactionRequestDTO import CASH_ASSET_TYPE
from services import price_service
from services.portfolio_item_service import PortfolioItemService
from utils.rounding import round_money


def _get_current_price(item: PortfolioItemDTO) -> Optional[float]:
    if item.assetType == CASH_ASSET_TYPE:
        return None
    return price_service.list_current_prices([item.ticker]).get(item.ticker)


def _to_result_dto(item: PortfolioItemDTO, current_price: Optional[float]) -> PortfolioItemResultDTO:
    """Compute currentPrice/marketValue/unrealizedPnL for one item.

    CASH has no price concept: currentPrice/unrealizedPnL stay None, but marketValue is just
    the quantity (1 unit of cash is worth 1 dollar, always at par). A ticker yfinance can't
    price gets currentPrice/marketValue/unrealizedPnL left as None (stale/unavailable) rather
    than failing the whole request.
    """
    is_cash = item.assetType == CASH_ASSET_TYPE
    if is_cash:
        market_value = round_money(item.quantity)
    else:
        market_value = None if current_price is None else round_money(item.quantity * current_price)
    unrealized_pnl = None if is_cash or market_value is None else round_money(market_value - item.costBasis)

    return PortfolioItemResultDTO(
        id=item.id,
        ticker=item.ticker,
        assetType=item.assetType,
        quantity=round_money(item.quantity),
        costBasis=round_money(item.costBasis),
        isFavourite=item.isFavourite,
        lastUpdated=item.lastUpdated.isoformat() if item.lastUpdated else None,
        currentPrice=None if is_cash else current_price,
        marketValue=market_value,
        unrealizedPnL=unrealized_pnl,
    )


class PortfolioService:
    """Business logic for viewing the portfolio as a whole (holdings + live pricing)."""

    @staticmethod
    def get_portfolio() -> list[PortfolioItemResultDTO]:
        """List all portfolio items with computed current price, market value, and unrealized P&L.

        An empty portfolio returns [] rather than an error.
        """
        items = PortfolioItemService.list_portfolio_items()
        if not items:
            return []

        tickers_to_price = [item.ticker for item in items if item.assetType != CASH_ASSET_TYPE]
        prices = price_service.list_current_prices(tickers_to_price) if tickers_to_price else {}

        return [_to_result_dto(item, prices.get(item.ticker)) for item in items]

    @staticmethod
    def get_portfolio_item(ticker: str, asset_type: str) -> Optional[PortfolioItemResultDTO]:
        """Get a single portfolio item by its natural key (ticker + assetType), with the same
        computed current price / market value / unrealized P&L as get_portfolio(). Returns
        None if no such item exists."""
        item = PortfolioItemService.get_portfolio_item_by_ticker_and_asset_type(ticker, asset_type)
        if item is None:
            return None
        return _to_result_dto(item, _get_current_price(item))

    @staticmethod
    def toggle_favourite(ticker: str, asset_type: str) -> Optional[PortfolioItemResultDTO]:
        """Flip isFavourite for a single portfolio item. Returns None if no such item exists."""
        item = PortfolioItemService.toggle_favourite(ticker, asset_type)
        if item is None:
            return None
        return _to_result_dto(item, _get_current_price(item))
