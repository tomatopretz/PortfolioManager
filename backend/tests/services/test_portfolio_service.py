import os
import sys
from datetime import datetime, timezone
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.PortfolioItemDTO import PortfolioItemDTO
from services import price_service
from services.portfolio_service import PortfolioService


def _item(ticker='AAPL', quantity=10, cost_basis=1000, asset_type='stock'):
    return PortfolioItemDTO(
        id='1', ticker=ticker, assetType=asset_type, quantity=quantity, costBasis=cost_basis,
        lastUpdated=datetime.now(timezone.utc),
    )


# --- raw CRUD - delegates straight to the repository, no pricing involved ------------------

@patch('services.portfolio_service.PortfolioItemRepository')
def test_get_portfolio_item_by_id_delegates_to_repository(mock_repo):
    mock_repo.get.return_value = _item()
    result = PortfolioService.get_portfolio_item_by_id('1')
    assert result.ticker == 'AAPL'
    mock_repo.get.assert_called_once_with('1')


@patch('services.portfolio_service.PortfolioItemRepository')
def test_get_portfolio_item_by_ticker_normalizes_case(mock_repo):
    mock_repo.get_by_ticker.return_value = _item()
    PortfolioService.get_portfolio_item_by_ticker('aapl')
    mock_repo.get_by_ticker.assert_called_once_with('AAPL')


@patch('services.portfolio_service.PortfolioItemRepository')
def test_list_portfolio_items_delegates_to_repository(mock_repo):
    mock_repo.list_all.return_value = [_item()]
    result = PortfolioService.list_portfolio_items()
    assert len(result) == 1
    mock_repo.list_all.assert_called_once_with()


@patch('services.portfolio_service.PortfolioItemRepository')
def test_add_portfolio_item_delegates_to_repository(mock_repo):
    item = _item()
    mock_repo.add.return_value = item
    result = PortfolioService.add_portfolio_item(item)
    assert result is item
    mock_repo.add.assert_called_once_with(item)


@patch('services.portfolio_service.PortfolioItemRepository')
def test_update_portfolio_item_delegates_to_repository(mock_repo):
    item = _item()
    mock_repo.update.return_value = item
    result = PortfolioService.update_portfolio_item(item)
    assert result is item
    mock_repo.update.assert_called_once_with(item)


@patch('services.portfolio_service.PortfolioItemRepository')
def test_delete_portfolio_item_delegates_to_repository(mock_repo):
    PortfolioService.delete_portfolio_item('1')
    mock_repo.delete.assert_called_once_with('1')


@patch('services.portfolio_service.PortfolioItemRepository')
def test_toggle_favourite_flips_false_to_true(mock_repo):
    item = _item()  # isFavourite defaults to False
    mock_repo.get_by_ticker_and_asset_type.return_value = item

    result = PortfolioService.toggle_favourite('aapl', 'stock')

    mock_repo.get_by_ticker_and_asset_type.assert_called_once_with('AAPL', 'STOCK')
    mock_repo.set_favourite.assert_called_once_with(item.id, True)
    assert result.isFavourite is True


@patch('services.portfolio_service.PortfolioItemRepository')
def test_toggle_favourite_flips_true_to_false(mock_repo):
    item = _item()
    item.isFavourite = True
    mock_repo.get_by_ticker_and_asset_type.return_value = item

    result = PortfolioService.toggle_favourite('aapl', 'stock')

    mock_repo.set_favourite.assert_called_once_with(item.id, False)
    assert result.isFavourite is False


@patch('services.portfolio_service.PortfolioItemRepository')
def test_toggle_favourite_returns_none_when_item_not_found(mock_repo):
    mock_repo.get_by_ticker_and_asset_type.return_value = None

    result = PortfolioService.toggle_favourite('aapl', 'stock')

    assert result is None
    mock_repo.set_favourite.assert_not_called()


# --- enriched "view" - always adds live pricing --------------------------------------------

@patch('services.portfolio_service.PortfolioService.list_portfolio_items')
def test_get_portfolio_returns_empty_list_for_empty_portfolio(mock_list_items):
    mock_list_items.return_value = []
    assert PortfolioService.get_enriched_portfolio() == []


@patch('services.portfolio_service.price_service.list_current_prices')
@patch('services.portfolio_service.PortfolioService.list_portfolio_items')
def test_get_portfolio_computes_market_value_and_pnl(mock_list_items, mock_list_prices):
    mock_list_items.return_value = [_item('AAPL', quantity=10, cost_basis=1000)]
    mock_list_prices.return_value = {'AAPL': 150.0}

    [result] = PortfolioService.get_enriched_portfolio()
    assert result.currentPrice == 150.0
    assert result.marketValue == 1500.0
    assert result.unrealizedPnL == 500.0
    mock_list_prices.assert_called_once_with(['AAPL'])


@patch('services.portfolio_service.price_service.list_current_prices')
@patch('services.portfolio_service.PortfolioService.list_portfolio_items')
def test_get_portfolio_cash_has_no_price_or_pnl(mock_list_items, mock_list_prices):
    mock_list_items.return_value = [_item('USD', quantity=500, cost_basis=500, asset_type='CASH')]
    mock_list_prices.return_value = {}

    [result] = PortfolioService.get_enriched_portfolio()
    assert result.currentPrice is None
    assert result.marketValue == 500  # cash marketValue is just its quantity, always at par
    assert result.unrealizedPnL is None
    mock_list_prices.assert_not_called()  # no non-CASH tickers, so no price lookup needed at all


@patch('services.portfolio_service.price_service.list_current_prices')
@patch('services.portfolio_service.PortfolioService.list_portfolio_items')
def test_get_portfolio_flags_unresolvable_ticker_as_stale(mock_list_items, mock_list_prices):
    mock_list_items.return_value = [_item('BADTICKER', quantity=5, cost_basis=100)]
    mock_list_prices.return_value = {}

    [result] = PortfolioService.get_enriched_portfolio()
    assert result.currentPrice is None
    assert result.marketValue is None
    assert result.unrealizedPnL is None


@patch('services.portfolio_service.PortfolioService.get_portfolio_item_by_ticker_and_asset_type')
def test_get_portfolio_item_returns_none_when_not_found(mock_get_item):
    mock_get_item.return_value = None
    assert PortfolioService.get_enriched_portfolio_item('AAPL', 'STOCK') is None


@patch('services.portfolio_service.price_service.get_current_price')
@patch('services.portfolio_service.PortfolioService.get_portfolio_item_by_ticker_and_asset_type')
def test_get_portfolio_item_computes_market_value_and_pnl(mock_get_item, mock_get_price):
    mock_get_item.return_value = _item('AAPL', quantity=10, cost_basis=1000)
    mock_get_price.return_value = 150.0

    result = PortfolioService.get_enriched_portfolio_item('AAPL', 'STOCK')
    assert result.currentPrice == 150.0
    assert result.marketValue == 1500.0
    assert result.unrealizedPnL == 500.0
    mock_get_price.assert_called_once_with('AAPL')


@patch('services.portfolio_service.price_service.get_current_price')
@patch('services.portfolio_service.PortfolioService.get_portfolio_item_by_ticker_and_asset_type')
def test_get_portfolio_item_cash_has_no_price_or_pnl(mock_get_item, mock_get_price):
    mock_get_item.return_value = _item('USD', quantity=500, cost_basis=500, asset_type='CASH')

    result = PortfolioService.get_enriched_portfolio_item('USD', 'CASH')
    assert result.currentPrice is None
    assert result.marketValue == 500
    assert result.unrealizedPnL is None
    mock_get_price.assert_not_called()  # CASH never needs a price lookup


@patch('services.portfolio_service.price_service.get_current_price')
@patch('services.portfolio_service.PortfolioService.get_portfolio_item_by_ticker_and_asset_type')
def test_get_portfolio_item_flags_unpriceable_ticker_as_stale(mock_get_item, mock_get_price):
    mock_get_item.return_value = _item('BADTICKER', quantity=5, cost_basis=100)
    mock_get_price.side_effect = price_service.PriceNotFoundError("No price data found for 'BADTICKER'")

    result = PortfolioService.get_enriched_portfolio_item('BADTICKER', 'STOCK')
    assert result.currentPrice is None
    assert result.marketValue is None
    assert result.unrealizedPnL is None
