import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.PortfolioItemDTO import PortfolioItemDTO
from services.portfolio_item_service import PortfolioItemService


def _item():
    return PortfolioItemDTO(id='1', ticker='AAPL', assetType='stock', quantity=10, costBasis=1000)


@patch('services.portfolio_item_service.PortfolioItemRepository')
def test_get_portfolio_item_delegates_to_repository(mock_repo):
    mock_repo.get.return_value = _item()
    result = PortfolioItemService.get_portfolio_item('1')
    assert result.ticker == 'AAPL'
    mock_repo.get.assert_called_once_with('1')


@patch('services.portfolio_item_service.PortfolioItemRepository')
def test_get_portfolio_item_by_ticker_normalizes_case(mock_repo):
    mock_repo.get_by_ticker.return_value = _item()
    PortfolioItemService.get_portfolio_item_by_ticker('aapl')
    mock_repo.get_by_ticker.assert_called_once_with('AAPL')


@patch('services.portfolio_item_service.PortfolioItemRepository')
def test_list_portfolio_items_delegates_to_repository(mock_repo):
    mock_repo.list_all.return_value = [_item()]
    result = PortfolioItemService.list_portfolio_items()
    assert len(result) == 1
    mock_repo.list_all.assert_called_once_with()


@patch('services.portfolio_item_service.PortfolioItemRepository')
def test_add_portfolio_item_delegates_to_repository(mock_repo):
    item = _item()
    mock_repo.add.return_value = item
    result = PortfolioItemService.add_portfolio_item(item)
    assert result is item
    mock_repo.add.assert_called_once_with(item)


@patch('services.portfolio_item_service.PortfolioItemRepository')
def test_update_portfolio_item_delegates_to_repository(mock_repo):
    item = _item()
    mock_repo.update.return_value = item
    result = PortfolioItemService.update_portfolio_item(item)
    assert result is item
    mock_repo.update.assert_called_once_with(item)


@patch('services.portfolio_item_service.PortfolioItemRepository')
def test_delete_portfolio_item_delegates_to_repository(mock_repo):
    PortfolioItemService.delete_portfolio_item('1')
    mock_repo.delete.assert_called_once_with('1')


@patch('services.portfolio_item_service.PortfolioItemRepository')
def test_toggle_favourite_flips_false_to_true(mock_repo):
    item = _item()  # isFavourite defaults to False
    mock_repo.get_by_ticker_and_asset_type.return_value = item

    result = PortfolioItemService.toggle_favourite('aapl', 'stock')

    mock_repo.get_by_ticker_and_asset_type.assert_called_once_with('AAPL', 'STOCK')
    mock_repo.set_favourite.assert_called_once_with(item.id, True)
    assert result.isFavourite is True


@patch('services.portfolio_item_service.PortfolioItemRepository')
def test_toggle_favourite_flips_true_to_false(mock_repo):
    item = _item()
    item.isFavourite = True
    mock_repo.get_by_ticker_and_asset_type.return_value = item

    result = PortfolioItemService.toggle_favourite('aapl', 'stock')

    mock_repo.set_favourite.assert_called_once_with(item.id, False)
    assert result.isFavourite is False


@patch('services.portfolio_item_service.PortfolioItemRepository')
def test_toggle_favourite_returns_none_when_item_not_found(mock_repo):
    mock_repo.get_by_ticker_and_asset_type.return_value = None

    result = PortfolioItemService.toggle_favourite('aapl', 'stock')

    assert result is None
    mock_repo.set_favourite.assert_not_called()
