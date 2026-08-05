from typing import Optional

from models.PortfolioItemDTO import PortfolioItemDTO
from models.PortfolioItemResultDTO import PortfolioItemResultDTO
from models.PortfolioResultDTO import PortfolioResultDTO
from models.RecordTransactionRequestDTO import CASH_ASSET_TYPE
from repository.portfolio_item_repository import PortfolioItemRepository
from services import price_service
from utils.rounding import round_money


def _to_result_dto(item: PortfolioItemDTO, current_price: Optional[float]) -> PortfolioItemResultDTO:
    """Compute currentPrice/marketValue/costBasisPerShare/pnl/gainLossPercent for one item.

    CASH is never "unpriced" - it's always worth $1.00 per unit at par, so currentPrice is a
    definite 1.0 and pnl/gainLossPercent are a definite 0, rather than None/unknown.
    """
    is_cash = item.assetType == CASH_ASSET_TYPE
    if is_cash:
        market_value = round_money(item.quantity)
        pnl = 0.0
        gain_loss_percent = 0.0
    else:
        market_value = None if current_price is None else round_money(item.quantity * current_price)
        pnl = None if market_value is None else round_money(market_value - item.costBasis)
        gain_loss_percent = None if pnl is None or not item.costBasis else round_money(pnl / item.costBasis * 100)

    cost_basis_per_share = None if not item.quantity else round_money(item.costBasis / item.quantity)

    return PortfolioItemResultDTO(
        id=item.id,
        ticker=item.ticker,
        assetType=item.assetType,
        quantity=round_money(item.quantity),
        costBasis=round_money(item.costBasis),
        isFavourite=item.isFavourite,
        lastUpdated=item.lastUpdated.isoformat() if item.lastUpdated else None,
        currentPrice=1.0 if is_cash else current_price,
        marketValue=market_value,
        costBasisPerShare=cost_basis_per_share,
        pnl=pnl,
        gainLossPercent=gain_loss_percent,
    )


class PortfolioService:
    """Business logic for portfolio items 

    - Get_enriched_portfolio() / get_enriched_portfolio_item() are the only two entry points that add live pricing
    (currentPrice/marketValue/pnl/gainLossPercent)
    - Every other method here is raw data access with no pricing involved
    """

    # --- raw CRUD on a single PortfolioItem - no live pricing, never calls price_service -----

    @staticmethod
    def get_portfolio_item_by_id(item_id: str) -> Optional[PortfolioItemDTO]:
        """Get a single portfolio item by id."""
        return PortfolioItemRepository.get(item_id)

    @staticmethod
    def get_portfolio_item_by_ticker_and_asset_type(ticker: str, asset_type: str) -> Optional[PortfolioItemDTO]:
        """Get a single portfolio item by its natural key (ticker + assetType)."""
        return PortfolioItemRepository.get_by_ticker_and_asset_type(ticker.upper(), asset_type.upper())

    @staticmethod
    def list_portfolio_items() -> list[PortfolioItemDTO]:
        """List all portfolio items (current holdings)."""
        return PortfolioItemRepository.list_all()

    @staticmethod
    def add_portfolio_item(item: PortfolioItemDTO) -> PortfolioItemDTO:
        """Create a new portfolio item."""
        return PortfolioItemRepository.add(item)

    @staticmethod
    def update_portfolio_item(item: PortfolioItemDTO) -> PortfolioItemDTO:
        """Update an existing portfolio item."""
        return PortfolioItemRepository.update(item)

    @staticmethod
    def toggle_favourite(ticker: str, asset_type: str) -> Optional[PortfolioItemDTO]:
        """Flip isFavourite for the item at this natural key. Returns None if no such item
        exists, otherwise the updated item."""
        item = PortfolioService.get_portfolio_item_by_ticker_and_asset_type(ticker, asset_type)
        if item is None:
            return None
        new_value = not item.isFavourite
        PortfolioItemRepository.set_favourite(item.id, new_value)
        item.isFavourite = new_value
        return item

    # --- enriched "view" - always adds live pricing ------------------------------------------

    @staticmethod
    def get_enriched_portfolio() -> PortfolioResultDTO:
        """List all portfolio items with computed current price, market value, and P&L, plus
        portfolio-wide totals (total market value, cash balance, total return $ and %).

        An empty portfolio returns an empty items list with all totals at 0, rather than an error.
        """
        items = PortfolioService.list_portfolio_items()
        if not items:
            return PortfolioResultDTO(
                items=[], totalValue=0, totalCashBalance=0, totalReturn=0, totalReturnPercent=0,
            )

        tickers_to_price = [item.ticker for item in items if item.assetType != CASH_ASSET_TYPE]
        prices = price_service.list_current_prices(tickers_to_price) if tickers_to_price else {}

        result_items = [_to_result_dto(item, prices.get(item.ticker)) for item in items]

        total_value = round_money(sum(item.marketValue or 0 for item in result_items))
        total_cash_balance = round_money(
            sum(item.marketValue or 0 for item in result_items if item.assetType == CASH_ASSET_TYPE)
        )
        total_return = round_money(sum(item.pnl or 0 for item in result_items))
        total_cost_basis = sum(item.costBasis for item in result_items)
        total_return_percent = round_money(total_return / total_cost_basis * 100) if total_cost_basis else 0.0

        return PortfolioResultDTO(
            items=result_items,
            totalValue=total_value,
            totalCashBalance=total_cash_balance,
            totalReturn=total_return,
            totalReturnPercent=total_return_percent,
        )

    @staticmethod
    def get_enriched_portfolio_item(ticker: str, asset_type: str) -> Optional[PortfolioItemResultDTO]:
        """Get a single portfolio item by its natural key (ticker + assetType), with the same
        computed current price / market value / P&L as get_enriched_portfolio() items.
        Returns None if no such item exists."""
        item = PortfolioService.get_portfolio_item_by_ticker_and_asset_type(ticker, asset_type)
        if item is None:
            return None

        current_price = None
        if item.assetType != CASH_ASSET_TYPE:
            try:
                current_price = price_service.get_current_price(item.ticker)
            except price_service.PriceNotFoundError:
                current_price = None

        return _to_result_dto(item, current_price)
