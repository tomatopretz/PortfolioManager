from datetime import datetime, timezone
from typing import Literal

from psycopg import Connection

from db import get_transaction
from models.PortfolioItemDTO import PortfolioItemDTO
from models.PortfolioItemResultDTO import PortfolioItemResultDTO
from models.PortfolioTransactionRequestDTO import CASH_ASSET_TYPE, CASH_TICKER, PortfolioTransactionRequestDTO
from models.TransactionDTO import TransactionDTO
from repository.portfolio_item_repository import PortfolioItemRepository
from repository.transaction_repository import TransactionRepository
from services import price_service
from services.portfolio_item_service import PortfolioItemService


class InsufficientCashError(ValueError):
    """Raised when a buy (useCash=True) or a cash withdrawal exceeds the available CASH balance."""


class InsufficientQuantityError(ValueError):
    """Raised when a sell requests more quantity than the PortfolioItem currently holds."""


class PortfolioItemNotFoundError(LookupError):
    """Raised when selling a ticker (or withdrawing CASH) with no existing PortfolioItem."""


def _is_cash(request: PortfolioTransactionRequestDTO) -> bool:
    # assetType arrives already upper-cased via PortfolioTransactionRequestDTO's validator
    return request.assetType == CASH_ASSET_TYPE


def _record_cash_movement(
    cash_id: str, movement_type: Literal['buy', 'sell'], amount: float, conn: Connection,
) -> TransactionDTO:
    """Insert a Transaction row for a change to the CASH item's balance - covers direct
    deposits/withdrawals, and the cash side of a stock/bond buy or sell."""
    return TransactionRepository.add(
        TransactionDTO(
            portfolioItemId=cash_id,
            type=movement_type,
            quantity=amount,
            price=1,
            date=datetime.now(timezone.utc),
            useCash=False,
        ),
        conn=conn,
    )


def _get_cash_item(conn: Connection) -> PortfolioItemDTO:
    """Fetch the CASH item, creating it with a zero balance if this is the first-ever movement."""
    cash = PortfolioItemRepository.get_by_ticker_and_asset_type(CASH_TICKER, CASH_ASSET_TYPE, conn=conn)
    if cash is not None:
        return cash
    return PortfolioItemRepository.add(
        PortfolioItemDTO(ticker=CASH_TICKER, assetType=CASH_ASSET_TYPE, quantity=0, costBasis=0),
        conn=conn,
    )


# --- ADD flow (type='buy'): buy stock/bond, or deposit cash --------------------------------

def _add_asset(request: PortfolioTransactionRequestDTO, conn: Connection) -> TransactionDTO:
    if _is_cash(request):
        return _deposit_cash(request, conn)
    return _buy_asset(request, conn)


def _deposit_cash(request: PortfolioTransactionRequestDTO, conn: Connection) -> TransactionDTO:
    cash = _get_cash_item(conn)
    cash.quantity += request.quantity
    cash.costBasis += request.quantity  # cash costBasis is always 1:1 with quantity
    PortfolioItemRepository.update(cash, conn=conn)

    return _record_cash_movement(cash.id, 'buy', request.quantity, conn)


def _buy_asset(request: PortfolioTransactionRequestDTO, conn: Connection) -> TransactionDTO:
    if request.useCash:
        cash = _get_cash_item(conn)
        cost = request.quantity * request.price
        if cash.quantity < cost:
            raise InsufficientCashError(
                f'CASH balance {cash.quantity} is less than purchase cost {cost}'
            )
        cash.quantity -= cost
        cash.costBasis -= cost  # cash costBasis always mirrors quantity 1:1
        PortfolioItemRepository.update(cash, conn=conn)
        _record_cash_movement(cash.id, 'sell', cost, conn)

    item = PortfolioItemRepository.get_by_ticker_and_asset_type(request.ticker, request.assetType, conn=conn)
    if item is not None:
        item.quantity += request.quantity
        item.costBasis += request.quantity * request.price
        PortfolioItemRepository.update(item, conn=conn)
    else:
        item = PortfolioItemRepository.add(
            PortfolioItemDTO(
                ticker=request.ticker,
                assetType=request.assetType,
                quantity=request.quantity,
                costBasis=request.quantity * request.price,
            ),
            conn=conn,
        )

    return TransactionRepository.add(
        TransactionDTO(
            portfolioItemId=item.id,
            type='buy',
            quantity=request.quantity,
            price=request.price,
            date=datetime.now(timezone.utc),
            useCash=request.useCash,
        ),
        conn=conn,
    )


# --- REMOVE flow (type='sell'): sell stock/bond, or withdraw cash --------------------------

def _remove_asset(request: PortfolioTransactionRequestDTO, conn: Connection) -> TransactionDTO:
    if _is_cash(request):
        return _withdraw_cash(request, conn)
    return _sell_asset(request, conn)


def _withdraw_cash(request: PortfolioTransactionRequestDTO, conn: Connection) -> TransactionDTO:
    cash = _get_cash_item(conn)
    if cash.quantity < request.quantity:
        raise InsufficientCashError(
            f'CASH balance {cash.quantity} is less than withdrawal amount {request.quantity}'
        )
    cash.quantity -= request.quantity
    cash.costBasis -= request.quantity
    PortfolioItemRepository.update(cash, conn=conn)

    return _record_cash_movement(cash.id, 'sell', request.quantity, conn)


def _sell_asset(request: PortfolioTransactionRequestDTO, conn: Connection) -> TransactionDTO:
    item = PortfolioItemRepository.get_by_ticker_and_asset_type(request.ticker, request.assetType, conn=conn)
    if item is None:
        raise PortfolioItemNotFoundError(
            f"No portfolio item found for ticker '{request.ticker}' ({request.assetType})"
        )
    if item.quantity < request.quantity:
        raise InsufficientQuantityError(
            f"Cannot sell {request.quantity} of '{request.ticker}': only {item.quantity} held"
        )

    proceeds = request.quantity * request.price
    cash = _get_cash_item(conn)
    cash.quantity += proceeds
    cash.costBasis += proceeds  # cash costBasis always mirrors quantity 1:1
    PortfolioItemRepository.update(cash, conn=conn)
    _record_cash_movement(cash.id, 'buy', proceeds, conn)

    cost_basis_per_share = item.costBasis / item.quantity
    new_quantity = item.quantity - request.quantity
    item.costBasis = cost_basis_per_share * new_quantity
    item.quantity = new_quantity
    # kept (at quantity 0) rather than deleted: transaction.portfolio_item_id is ON DELETE
    # CASCADE, so deleting this row would wipe every transaction ever recorded against it
    PortfolioItemRepository.update(item, conn=conn)

    return TransactionRepository.add(
        TransactionDTO(
            portfolioItemId=item.id,
            type='sell',
            quantity=request.quantity,
            price=request.price,
            date=datetime.now(timezone.utc),
            useCash=True,
        ),
        conn=conn,
    )


class PortfolioService:
    """Business logic for viewing the portfolio as a whole (holdings + live pricing)."""

    @staticmethod
    def get_portfolio() -> list[PortfolioItemResultDTO]:
        """List all portfolio items with computed current price, market value, and unrealized P&L.

        Edge cases:
        - CASH has no price concept: currentPrice/unrealizedPnL stay None, but marketValue is
          just the quantity (1 unit of cash is worth 1 dollar, always at par).
        - An empty portfolio returns [] rather than an error.
        - A ticker yfinance can't price gets currentPrice/marketValue/unrealizedPnL left as None
          (stale/unavailable) rather than failing the whole request.
        """
        items = PortfolioItemService.list_portfolio_items()
        if not items:
            return []

        tickers_to_price = [item.ticker for item in items if item.assetType != CASH_ASSET_TYPE]
        prices = price_service.list_current_prices(tickers_to_price) if tickers_to_price else {}

        result = []
        for item in items:
            is_cash = item.assetType == CASH_ASSET_TYPE
            current_price = None if is_cash else prices.get(item.ticker)

            if is_cash:
                market_value = item.quantity
            else:
                market_value = None if current_price is None else round(item.quantity * current_price, 2)
            unrealized_pnl = None if is_cash or market_value is None else round(market_value - item.costBasis, 2)

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

    @staticmethod
    def record_transaction(request: PortfolioTransactionRequestDTO) -> TransactionDTO:
        """Record a buy (add asset / deposit cash) or sell (remove asset / withdraw cash).

        Every step runs inside a single DB transaction so a failure partway through
        (e.g. insufficient cash discovered after a lookup) rolls back cleanly.
        """
        with get_transaction() as conn:
            if request.type == 'buy':
                return _add_asset(request, conn)
            return _remove_asset(request, conn)
