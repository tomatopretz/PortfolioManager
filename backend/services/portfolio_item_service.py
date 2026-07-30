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
