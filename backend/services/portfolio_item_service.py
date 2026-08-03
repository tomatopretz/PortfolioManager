from typing import Optional

from models.PortfolioItemDTO import PortfolioItemDTO
from repository.portfolio_item_repository import PortfolioItemRepository


class PortfolioItemService:
    """Business logic for portfolio items."""

    @staticmethod
    def get_portfolio_item(item_id: str) -> Optional[PortfolioItemDTO]:
        """Get a single portfolio item by id."""
        return PortfolioItemRepository.get(item_id)

    @staticmethod
    def get_portfolio_item_by_ticker(ticker: str) -> Optional[PortfolioItemDTO]:
        """Get a single portfolio item by ticker."""
        return PortfolioItemRepository.get_by_ticker(ticker.upper())

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
    def delete_portfolio_item(item_id: str) -> None:
        """Delete a portfolio item."""
        PortfolioItemRepository.delete(item_id)

    @staticmethod
    def toggle_favourite(ticker: str, asset_type: str) -> Optional[PortfolioItemDTO]:
        """Flip isFavourite for the item at this natural key. Returns None if no such item
        exists, otherwise the updated item."""
        item = PortfolioItemService.get_portfolio_item_by_ticker_and_asset_type(ticker, asset_type)
        if item is None:
            return None
        new_value = not item.isFavourite
        PortfolioItemRepository.set_favourite(item.id, new_value)
        item.isFavourite = new_value
        return item
