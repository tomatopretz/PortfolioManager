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

@patch('services.portfolio_service.PortfolioItemRepository')  # mock: replace the whole repository class
def test_get_portfolio_item_by_id_delegates_to_repository(mock_repo):
    # Given the repository returns an item
    mock_repo.get.return_value = _item()
    # When/Then fetching by id just forwards to the repository and returns its result
    result = PortfolioService.get_portfolio_item_by_id('1')
    assert result.ticker == 'AAPL'
    mock_repo.get.assert_called_once_with('1')


@patch('services.portfolio_service.PortfolioItemRepository')  # mock: replace the whole repository class
def test_list_portfolio_items_delegates_to_repository(mock_repo):
    # Given the repository returns one item
    mock_repo.list_all.return_value = [_item()]
    # When/Then listing items just forwards to the repository and returns its result
    result = PortfolioService.list_portfolio_items()
    assert len(result) == 1
    mock_repo.list_all.assert_called_once_with()


@patch('services.portfolio_service.PortfolioItemRepository')  # mock: replace the whole repository class
def test_add_portfolio_item_delegates_to_repository(mock_repo):
    # Given the repository echoes back the item it was given
    item = _item()
    mock_repo.add.return_value = item
    # When/Then adding an item just forwards to the repository and returns its result
    result = PortfolioService.add_portfolio_item(item)
    assert result is item
    mock_repo.add.assert_called_once_with(item)


@patch('services.portfolio_service.PortfolioItemRepository')  # mock: replace the whole repository class
def test_update_portfolio_item_delegates_to_repository(mock_repo):
    # Given the repository echoes back the item it was given
    item = _item()
    mock_repo.update.return_value = item
    # When/Then updating an item just forwards to the repository and returns its result
    result = PortfolioService.update_portfolio_item(item)
    assert result is item
    mock_repo.update.assert_called_once_with(item)


@patch('services.portfolio_service.PortfolioItemRepository')  # mock: replace the whole repository class
def test_toggle_favourite_flips_false_to_true(mock_repo):
    # Given an item with isFavourite currently False
    item = _item()  # isFavourite defaults to False
    mock_repo.get_by_ticker_and_asset_type.return_value = item

    # When toggling its favourite flag
    result = PortfolioService.toggle_favourite('aapl', 'stock')

    # Then it flips to True and is persisted via set_favourite
    mock_repo.get_by_ticker_and_asset_type.assert_called_once_with('AAPL', 'STOCK')
    mock_repo.set_favourite.assert_called_once_with(item.id, True)
    assert result.isFavourite is True


@patch('services.portfolio_service.PortfolioItemRepository')  # mock: replace the whole repository class
def test_toggle_favourite_flips_true_to_false(mock_repo):
    # Given an item with isFavourite currently True
    item = _item()
    item.isFavourite = True
    mock_repo.get_by_ticker_and_asset_type.return_value = item

    # When toggling its favourite flag
    result = PortfolioService.toggle_favourite('aapl', 'stock')

    # Then it flips to False and is persisted via set_favourite
    mock_repo.set_favourite.assert_called_once_with(item.id, False)
    assert result.isFavourite is False


@patch('services.portfolio_service.PortfolioItemRepository')  # mock: replace the whole repository class
def test_toggle_favourite_returns_none_when_item_not_found(mock_repo):
    # Given no item exists at that ticker/assetType
    mock_repo.get_by_ticker_and_asset_type.return_value = None

    # When toggling its favourite flag
    result = PortfolioService.toggle_favourite('aapl', 'stock')

    # Then nothing is persisted and None is returned
    assert result is None
    mock_repo.set_favourite.assert_not_called()


# --- enriched "view" - always adds live pricing --------------------------------------------

@patch('services.portfolio_service.PortfolioService.list_portfolio_items')  # mock: skip the real repository call
def test_get_portfolio_returns_empty_list_for_empty_portfolio(mock_list_items):
    # Given there are no portfolio items at all
    mock_list_items.return_value = []
    # When/Then the enriched portfolio is [] rather than an error
    assert PortfolioService.get_enriched_portfolio() == []


@patch('services.portfolio_service.price_service.list_current_prices')  # mock: skip the real yfinance call
@patch('services.portfolio_service.PortfolioService.list_portfolio_items')  # mock: skip the real repository call
def test_get_portfolio_computes_market_value_and_pnl(mock_list_items, mock_list_prices):
    # Given one AAPL holding and a current price for it
    mock_list_items.return_value = [_item('AAPL', quantity=10, cost_basis=1000)]
    mock_list_prices.return_value = {'AAPL': 150.0}

    # When/Then the enriched item has currentPrice/marketValue/unrealizedPnL computed from it
    [result] = PortfolioService.get_enriched_portfolio()
    assert result.currentPrice == 150.0
    assert result.marketValue == 1500.0
    assert result.unrealizedPnL == 500.0
    mock_list_prices.assert_called_once_with(['AAPL'])


@patch('services.portfolio_service.price_service.list_current_prices')  # mock: skip the real yfinance call
@patch('services.portfolio_service.PortfolioService.list_portfolio_items')  # mock: skip the real repository call
def test_get_portfolio_cash_has_no_price_or_pnl(mock_list_items, mock_list_prices):
    # Given the only holding is CASH
    mock_list_items.return_value = [_item('USD', quantity=500, cost_basis=500, asset_type='CASH')]
    mock_list_prices.return_value = {}

    # When/Then CASH gets no price/P&L, and marketValue is just its quantity (always at par)
    [result] = PortfolioService.get_enriched_portfolio()
    assert result.currentPrice is None
    assert result.marketValue == 500  # cash marketValue is just its quantity, always at par
    assert result.unrealizedPnL is None
    mock_list_prices.assert_not_called()  # no non-CASH tickers, so no price lookup needed at all


@patch('services.portfolio_service.price_service.list_current_prices')  # mock: skip the real yfinance call
@patch('services.portfolio_service.PortfolioService.list_portfolio_items')  # mock: skip the real repository call
def test_get_portfolio_flags_unresolvable_ticker_as_stale(mock_list_items, mock_list_prices):
    # Given a holding whose ticker the price service can't resolve
    mock_list_items.return_value = [_item('BADTICKER', quantity=5, cost_basis=100)]
    mock_list_prices.return_value = {}

    # When/Then price/marketValue/P&L are all None instead of raising
    [result] = PortfolioService.get_enriched_portfolio()
    assert result.currentPrice is None
    assert result.marketValue is None
    assert result.unrealizedPnL is None


@patch('services.portfolio_service.PortfolioService.get_portfolio_item_by_ticker_and_asset_type')  # mock: skip the real repository call
def test_get_portfolio_item_returns_none_when_not_found(mock_get_item):
    # Given no item exists at that ticker/assetType
    mock_get_item.return_value = None
    # When/Then the enriched lookup returns None rather than raising
    assert PortfolioService.get_enriched_portfolio_item('AAPL', 'STOCK') is None


@patch('services.portfolio_service.price_service.get_current_price')  # mock: skip the real yfinance call
@patch('services.portfolio_service.PortfolioService.get_portfolio_item_by_ticker_and_asset_type')  # mock: skip the real repository call
def test_get_portfolio_item_computes_market_value_and_pnl(mock_get_item, mock_get_price):
    # Given the AAPL item exists and has a current price
    mock_get_item.return_value = _item('AAPL', quantity=10, cost_basis=1000)
    mock_get_price.return_value = 150.0

    # When/Then the enriched item has currentPrice/marketValue/unrealizedPnL computed from it
    result = PortfolioService.get_enriched_portfolio_item('AAPL', 'STOCK')
    assert result.currentPrice == 150.0
    assert result.marketValue == 1500.0
    assert result.unrealizedPnL == 500.0
    mock_get_price.assert_called_once_with('AAPL')


@patch('services.portfolio_service.price_service.get_current_price')  # mock: skip the real yfinance call
@patch('services.portfolio_service.PortfolioService.get_portfolio_item_by_ticker_and_asset_type')  # mock: skip the real repository call
def test_get_portfolio_item_cash_has_no_price_or_pnl(mock_get_item, mock_get_price):
    # Given the item is CASH
    mock_get_item.return_value = _item('USD', quantity=500, cost_basis=500, asset_type='CASH')

    # When/Then CASH gets no price/P&L, and marketValue is just its quantity - no price lookup happens
    result = PortfolioService.get_enriched_portfolio_item('USD', 'CASH')
    assert result.currentPrice is None
    assert result.marketValue == 500
    assert result.unrealizedPnL is None
    mock_get_price.assert_not_called()  # CASH never needs a price lookup


@patch('services.portfolio_service.price_service.get_current_price')  # mock: skip the real yfinance call
@patch('services.portfolio_service.PortfolioService.get_portfolio_item_by_ticker_and_asset_type')  # mock: skip the real repository call
def test_get_portfolio_item_flags_unpriceable_ticker_as_stale(mock_get_item, mock_get_price):
    # Given the item's ticker has no resolvable price
    mock_get_item.return_value = _item('BADTICKER', quantity=5, cost_basis=100)
    mock_get_price.side_effect = price_service.PriceNotFoundError("No price data found for 'BADTICKER'")

    # When/Then price/marketValue/P&L are all None instead of raising
    result = PortfolioService.get_enriched_portfolio_item('BADTICKER', 'STOCK')
    assert result.currentPrice is None
    assert result.marketValue is None
    assert result.unrealizedPnL is None
