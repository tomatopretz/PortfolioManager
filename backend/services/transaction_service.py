from datetime import datetime, timezone
from typing import Literal, Optional

from psycopg import Connection

from db import get_transaction
from models.PortfolioItemDTO import PortfolioItemDTO
from models.RecordTransactionRequestDTO import CASH_ASSET_TYPE, CASH_TICKER, RecordTransactionRequestDTO
from models.TransactionDTO import TransactionDTO
from repository.portfolio_item_repository import PortfolioItemRepository
from repository.transaction_repository import TransactionRepository
from utils.rounding import round_money


class InsufficientCashError(ValueError):
    """Raised when a buy (useCash=True) or a cash withdrawal exceeds the available CASH balance."""


class InsufficientQuantityError(ValueError):
    """Raised when a sell requests more quantity than the PortfolioItem currently holds."""


class PortfolioItemNotFoundError(LookupError):
    """Raised when selling a ticker (or withdrawing CASH) with no existing PortfolioItem."""


def _is_cash(request: RecordTransactionRequestDTO) -> bool:
    # assetType arrives already upper-cased via RecordTransactionRequestDTO's validator
    return request.assetType == CASH_ASSET_TYPE


def _record_cash_movement(
    cash_id: str, movement_type: Literal['buy', 'sell'], amount: float, date: datetime, conn: Connection,
) -> TransactionDTO:
    """Insert a Transaction row for a change to the CASH item's balance - covers direct
    deposits/withdrawals, and the cash side of a stock/bond buy or sell."""
    return TransactionRepository.add(
        TransactionDTO(
            portfolioItemId=cash_id,
            type=movement_type,
            quantity=amount,
            price=1,
            date=date,
            useCash=False,
        ),
        conn=conn,
    )


def _get_cash_item(conn: Connection) -> PortfolioItemDTO:
    """Fetch the CASH item (locked for update - see record_transaction's docstring for why),
    creating it with a zero balance if this is the first-ever movement."""
    cash = PortfolioItemRepository.get_by_ticker_and_asset_type(
        CASH_TICKER, CASH_ASSET_TYPE, conn=conn, for_update=True,
    )
    if cash is not None:
        return cash
    return PortfolioItemRepository.add(
        PortfolioItemDTO(ticker=CASH_TICKER, assetType=CASH_ASSET_TYPE, quantity=0, costBasis=0),
        conn=conn,
    )


# --- ADD flow (type='buy'): buy stock/bond, or deposit cash --------------------------------

def _add_asset(request: RecordTransactionRequestDTO, date: datetime, conn: Connection) -> TransactionDTO:
    if _is_cash(request):
        return _deposit_cash(request, date, conn)
    return _buy_asset(request, date, conn)


def _deposit_cash(request: RecordTransactionRequestDTO, date: datetime, conn: Connection) -> TransactionDTO:
    cash = _get_cash_item(conn)
    cash.quantity = round_money(cash.quantity + request.quantity)
    cash.costBasis = round_money(cash.costBasis + request.quantity)  # cash costBasis is always 1:1 with quantity
    PortfolioItemRepository.update(cash, conn=conn)

    return _record_cash_movement(cash.id, 'buy', request.quantity, date, conn)


def _buy_asset(request: RecordTransactionRequestDTO, date: datetime, conn: Connection) -> TransactionDTO:
    if request.useCash:
        cash = _get_cash_item(conn)
        cost = round_money(request.quantity * request.price)
        if cash.quantity < cost:
            raise InsufficientCashError(
                f'CASH balance {cash.quantity} is less than purchase cost {cost}'
            )
        cash.quantity = round_money(cash.quantity - cost)
        cash.costBasis = round_money(cash.costBasis - cost)  # cash costBasis always mirrors quantity 1:1
        PortfolioItemRepository.update(cash, conn=conn)
        _record_cash_movement(cash.id, 'sell', cost, date, conn)

    item = PortfolioItemRepository.get_by_ticker_and_asset_type(
        request.ticker, request.assetType, conn=conn, for_update=True,
    )
    if item is not None:
        item.quantity = round_money(item.quantity + request.quantity)
        item.costBasis = round_money(item.costBasis + request.quantity * request.price)
        PortfolioItemRepository.update(item, conn=conn)
    else:
        item = PortfolioItemRepository.add(
            PortfolioItemDTO(
                ticker=request.ticker,
                assetType=request.assetType,
                quantity=round_money(request.quantity),
                costBasis=round_money(request.quantity * request.price),
            ),
            conn=conn,
        )

    return TransactionRepository.add(
        TransactionDTO(
            portfolioItemId=item.id,
            type='buy',
            quantity=request.quantity,
            price=request.price,
            date=date,
            useCash=request.useCash,
        ),
        conn=conn,
    )


# --- REMOVE flow (type='sell'): sell stock/bond, or withdraw cash --------------------------

def _remove_asset(request: RecordTransactionRequestDTO, date: datetime, conn: Connection) -> TransactionDTO:
    if _is_cash(request):
        return _withdraw_cash(request, date, conn)
    return _sell_asset(request, date, conn)


def _withdraw_cash(request: RecordTransactionRequestDTO, date: datetime, conn: Connection) -> TransactionDTO:
    cash = _get_cash_item(conn)
    if cash.quantity < request.quantity:
        raise InsufficientCashError(
            f'CASH balance {cash.quantity} is less than withdrawal amount {request.quantity}'
        )
    cash.quantity = round_money(cash.quantity - request.quantity)
    cash.costBasis = round_money(cash.costBasis - request.quantity)
    PortfolioItemRepository.update(cash, conn=conn)

    return _record_cash_movement(cash.id, 'sell', request.quantity, date, conn)


def _sell_asset(request: RecordTransactionRequestDTO, date: datetime, conn: Connection) -> TransactionDTO:
    # lock CASH before the stock/bond row, same order _buy_asset uses - see point 3 in
    # record_transaction's docstring for why the order has to match across code paths
    cash = _get_cash_item(conn)
    item = PortfolioItemRepository.get_by_ticker_and_asset_type(
        request.ticker, request.assetType, conn=conn, for_update=True,
    )
    if item is None:
        raise PortfolioItemNotFoundError(
            f"No portfolio item found for ticker '{request.ticker}' ({request.assetType})"
        )
    if item.quantity < request.quantity:
        raise InsufficientQuantityError(
            f"Cannot sell {request.quantity} of '{request.ticker}': only {item.quantity} held"
        )

    proceeds = round_money(request.quantity * request.price)
    cash.quantity = round_money(cash.quantity + proceeds)
    cash.costBasis = round_money(cash.costBasis + proceeds)  # cash costBasis always mirrors quantity 1:1
    PortfolioItemRepository.update(cash, conn=conn)
    _record_cash_movement(cash.id, 'buy', proceeds, date, conn)

    cost_basis_per_share = item.costBasis / item.quantity
    new_quantity = round_money(item.quantity - request.quantity)
    item.costBasis = round_money(cost_basis_per_share * new_quantity)
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
            date=date,
            useCash=True,
        ),
        conn=conn,
    )


class TransactionService:
    """Business logic for transactions - the source of truth that PortfolioItem balances are
    derived from."""

    @staticmethod
    def list_transactions(tickers: Optional[list[str]] = None) -> list[TransactionDTO]:
        """List all recorded transactions, optionally filtered to one or more tickers."""
        if not tickers:
            return TransactionRepository.list_all()
        return TransactionRepository.list_by_tickers(tickers)

    @staticmethod
    def record_transaction(request: RecordTransactionRequestDTO) -> TransactionDTO:
        """Record a buy (add asset / deposit cash) or sell (remove asset / withdraw cash).

        This touches two rows (CASH and/or a stock/bond PortfolioItem) plus one or two new
        Transaction rows, and has to stay correct even when many requests hit it at once.
        """
        date = request.date or datetime.now(timezone.utc)
        with get_transaction() as conn:
            if request.type == 'buy':
                return _add_asset(request, date, conn)
            return _remove_asset(request, date, conn)
