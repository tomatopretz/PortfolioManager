<<<<<<< HEAD
from models.PortfolioItemResultDTO import PortfolioItemResultDTO
from services import price_service
from services.portfolio_item_service import PortfolioItemService

CASH_TICKER = 'CASH'


class PortfolioService:
    """Business logic for viewing the portfolio as a whole (holdings + live pricing)."""

    @staticmethod
    def get_portfolio() -> list[PortfolioItemResultDTO]:
        """List all portfolio items with computed current price, market value, and unrealized P&L.

        Edge cases:
        - CASH has no price concept: currentPrice/marketValue/unrealizedPnL are all None.
        - An empty portfolio returns [] rather than an error.
        - A ticker yfinance can't price gets currentPrice/marketValue/unrealizedPnL left as None
          (stale/unavailable) rather than failing the whole request.
        """
        items = PortfolioItemService.list_portfolio_items()
        if not items:
            return []

        tickers_to_price = [item.ticker for item in items if item.ticker != CASH_TICKER]
        prices = price_service.list_current_prices(tickers_to_price) if tickers_to_price else {}

        result = []
        for item in items:
            current_price = None if item.ticker == CASH_TICKER else prices.get(item.ticker)
            market_value = None if current_price is None else round(item.quantity * current_price, 2)
            unrealized_pnl = None if market_value is None else round(market_value - item.costBasis, 2)

            result.append(PortfolioItemResultDTO(
                id=item.id,
                ticker=item.ticker,
                assetType=item.assetType,
                quantity=item.quantity,
                costBasis=item.costBasis,
                lastUpdated=item.lastUpdated.isoformat() if item.lastUpdated else None,
                currentPrice=current_price,
                marketValue=market_value,
                unrealizedPnL=unrealized_pnl,
            ))
        return result
=======
from models.PortfolioItemResultDTO import PortfolioItemResultDTO
from services import price_service
from services.portfolio_item_service import PortfolioItemService

CASH_TICKER = 'CASH'


class PortfolioService:
    """Business logic for viewing the portfolio as a whole (holdings + live pricing)."""

    @staticmethod
    def get_portfolio() -> list[PortfolioItemResultDTO]:
        """List all portfolio items with computed current price, market value, and unrealized P&L.

        Edge cases:
        - CASH has no price concept: currentPrice/marketValue/unrealizedPnL are all None.
        - An empty portfolio returns [] rather than an error.
        - A ticker yfinance can't price gets currentPrice/marketValue/unrealizedPnL left as None
          (stale/unavailable) rather than failing the whole request.
        """
        items = PortfolioItemService.list_portfolio_items()
        if not items:
            return []

        tickers_to_price = [item.ticker for item in items if item.ticker != CASH_TICKER]
        prices = price_service.list_current_prices(tickers_to_price) if tickers_to_price else {}

        result = []
        for item in items:
            current_price = None if item.ticker == CASH_TICKER else prices.get(item.ticker)
            market_value = None if current_price is None else round(item.quantity * current_price, 2)
            unrealized_pnl = None if market_value is None else round(market_value - item.costBasis, 2)

            result.append(PortfolioItemResultDTO(
                id=item.id,
                ticker=item.ticker,
                assetType=item.assetType,
                quantity=item.quantity,
                costBasis=item.costBasis,
                isFavourite=item.isFavourite,
                lastUpdated=item.lastUpdated.isoformat() if item.lastUpdated else None,
                currentPrice=current_price,
                marketValue=market_value,
                unrealizedPnL=unrealized_pnl,
            ))
        return result
>>>>>>> main
