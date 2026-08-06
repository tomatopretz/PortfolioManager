import csv
from datetime import datetime, timezone
from io import StringIO
from typing import Literal, Optional

from psycopg import Connection

from db import get_transaction
from models.PortfolioItemDTO import PortfolioItemDTO
from models.RecordTransactionRequestDTO import CASH_ASSET_TYPE, CASH_TICKER, RecordTransactionRequestDTO
from models.TransactionDTO import TransactionDTO
from repository.portfolio_item_repository import PortfolioItemRepository
from repository.transaction_repository import TransactionRepository
from utils.rounding import round_money


class InsufficientBalanceError(ValueError):
    """Raised when a debit (funded buy, withdrawal, or sell) exceeds CASH or quantity available."""


class PortfolioItemNotFoundError(LookupError):
    """Raised when selling a ticker (or withdrawing CASH) with no existing PortfolioItem."""


_EPSILON = 1e-9  # tolerance for float rounding noise when comparing a running balance to zero
_CSV_HEADERS = ('Date', 'Ticker', 'Type', 'Action', 'Quantity', 'Price', 'UseCash')


class TransactionService:
    """Business logic for transactions - the source of truth that PortfolioItem balances are derived from."""

    @staticmethod
    def list_transactions(tickers: Optional[list[str]] = None) -> list[TransactionDTO]:
        """List all recorded transactions, optionally filtered to one or more tickers."""
        if not tickers:
            return TransactionRepository.list_all()
        return TransactionRepository.list_by_tickers(tickers)

    @staticmethod
    def record_transaction(request: RecordTransactionRequestDTO) -> TransactionDTO:
        """Record a buy (add asset / deposit cash) or sell (remove asset / withdraw cash)."""
        date = request.date or datetime.now(timezone.utc)
        with get_transaction() as conn:
            if request.type == 'buy':
                return _add_asset(request, date, conn)
            return _remove_asset(request, date, conn)

    @staticmethod
    def record_transactions_bulk(requests: list[RecordTransactionRequestDTO]) -> list[TransactionDTO]:
        """Record many transactions inside one DB transaction.

        Deliberately duplicates record_transaction's tiny dispatch so this bulk endpoint can be
        removed without touching the single-transaction path.
        """
        created = []
        default_date = datetime.now(timezone.utc)
        sorted_requests = sorted(
            enumerate(requests),
            key=lambda item: (item[1].date or default_date, item[0]),
        )
        with get_transaction() as conn:
            for _, request in sorted_requests:
                date = request.date or default_date
                if request.type == 'buy':
                    created.append(_add_asset(request, date, conn))
                else:
                    created.append(_remove_asset(request, date, conn))
        return created

    @staticmethod
    def export_transactions_csv() -> str:
        """Export transaction history as CSV, including direct cash deposits/withdrawals."""
        output = StringIO()
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(_CSV_HEADERS)

        for row in TransactionRepository.list_export_rows():
            is_cash = row['assetType'] == CASH_ASSET_TYPE
            action = row['type']
            if is_cash:
                action = 'deposit' if row['type'] == 'buy' else 'withdrawal'

            writer.writerow(
                [
                    row['date'].date().isoformat(),
                    row['ticker'],
                    row['assetType'],
                    action.upper(),
                    row['quantity'],
                    row['price'],
                    'TRUE' if row['useCash'] else 'FALSE',
                ]
            )

        return output.getvalue()



# --- REPLAY logic for debitting cash/asset --------------------------------

def _running_quantities(transactions: list[TransactionDTO]) -> list[float]:
    """Replay a chronologically-sorted transaction list, returning the running quantity after each one."""
    running = 0.0
    history = []
    for txn in transactions:
        direction = 1 if txn.type == 'buy' else -1
        running = round_money(running + direction * txn.quantity)
        history.append(running)
    return history


def _same_date_priority(txn: TransactionDTO, is_cash: bool) -> int:
    """Tie-break order for transactions sharing the exact same date - `date` alone doesn't say
    which happened first, so pick the order most likely to keep a same-day sequence valid."""
    if not is_cash:
        # a non-CASH item only ever has buys and sells of itself: buy before sell
        is_buy = txn.type == 'buy'
        return 0 if is_buy else 1

    # on CASH's own history, "buy"/"sell" mean four different things depending on `useCash`:
    is_deposit = txn.type == 'buy' and not txn.useCash
    is_debit_from_a_buy_elsewhere = txn.type == 'sell' and txn.useCash
    is_credit_from_a_sell_elsewhere = txn.type == 'buy' and txn.useCash
    is_withdrawal = txn.type == 'sell' and not txn.useCash

    if is_deposit:
        return 0
    if is_debit_from_a_buy_elsewhere:
        return 1
    if is_credit_from_a_sell_elsewhere:
        return 2
    assert is_withdrawal
    return 3


def _validate_debit(
    item: PortfolioItemDTO, amount: float, date: datetime, conn: Connection, label: str, useCash: bool = True,
) -> None:
    """Raise InsufficientBalanceError if debiting `amount` from `item` at `date` would ever leave it negative.

    - Cheap reject: a debit anywhere shifts the final balance by -amount, so if today's quantity
      can't cover it, it's invalid regardless of date - no query needed.
    - Not backdated: that check alone is enough, since nothing later depends on this point.
    - Backdated: replay the full history with this inserted, checking every point stays >= 0 -
      an earlier debit can retroactively invalidate a later transaction even if the final
      balance still looks fine."""
    if round_money(item.quantity - amount) < -_EPSILON:
        raise InsufficientBalanceError(f'{label} {item.quantity} is less than the {amount} required')

    latest_date = TransactionRepository.get_latest_date(item.id, conn=conn)
    if latest_date is None or date >= latest_date:
        return

    is_cash = item.ticker == CASH_TICKER
    prospective = TransactionDTO(portfolioItemId=item.id, type='sell', quantity=amount, price=1, date=date, useCash=useCash)
    existing = TransactionRepository.list_by_portfolio_item(item.id, conn=conn)
    # combine and sort by (date, same-day category) - date alone leaves same-day ties undefined
    combined = sorted(existing + [prospective], key=lambda t: (t.date, _same_date_priority(t, is_cash)))
    for txn, balance in zip(combined, _running_quantities(combined)):
        if balance < -_EPSILON:
            raise InsufficientBalanceError(
                f'{label} would go negative ({balance}) as of the {txn.date} transaction'
            )
        
def _is_backdated(item: PortfolioItemDTO, date: datetime, conn: Connection) -> bool:
    """True when `date` falls before the item's latest recorded transaction - i.e. this
    transaction happened before something already on record, so it needs to be folded into
    history at the point it actually occurred rather than just appended on top of the current
    running totals."""
    latest_date = TransactionRepository.get_latest_date(item.id, conn=conn)
    return latest_date is not None and date < latest_date


def _recompute_cost_basis_for_backdated_transaction(item: PortfolioItemDTO, conn: Connection) -> None:
    """Rebuild item.quantity/costBasis by replaying its full transaction history in order.

    - A backdated buy/sell of stock/bond can't just be added onto the current totals - a sell already on
      record may have used the wrong average cost before this transaction was known about
    - Call only after the new transaction is inserted, so the replay includes it"""
    transactions = TransactionRepository.list_by_portfolio_item(item.id, conn=conn)  # every txn ever recorded for this item
    history = sorted(transactions, key=lambda t: (t.date, _same_date_priority(t, is_cash=False)))  # true chronological order, same-day ties broken buy-before-sell

    quantity = 0.0  # running share count, rebuilt from zero
    cost_basis = 0.0  # running total $ paid, rebuilt from zero
    for txn in history:  # replay every transaction in order, oldest first
        if txn.type == 'buy':
            quantity = round_money(quantity + txn.quantity)  # add the shares bought
            cost_basis = round_money(cost_basis + txn.quantity * txn.price)  # add what was paid for them
        else:
            cost_basis_per_share = cost_basis / quantity if quantity else 0.0  # average cost at this point in history
            quantity = round_money(quantity - txn.quantity)  # remove the shares sold
            cost_basis = round_money(cost_basis_per_share * quantity)  # shrink cost basis to match what's left, at that average

    item.quantity = quantity  # final replayed quantity replaces whatever was there before
    item.costBasis = cost_basis  # final replayed cost basis replaces whatever was there before
    PortfolioItemRepository.update(item, conn=conn)  # persist the corrected totals


# --- Cash helpers - debit and credit cash --------------------------------


def _is_cash(request: RecordTransactionRequestDTO) -> bool:
    # assetType arrives already upper-cased via RecordTransactionRequestDTO's validator
    return request.assetType == CASH_ASSET_TYPE


def _record_cash_movement(
    cash_id: str, movement_type: Literal['buy', 'sell'], amount: float, date: datetime, conn: Connection,
    useCash: bool = False,
) -> TransactionDTO:
    """Insert a Transaction row for a change to the CASH item's balance."""
    return TransactionRepository.add(
        TransactionDTO(
            portfolioItemId=cash_id,
            type=movement_type,
            quantity=amount,
            price=1,
            date=date,
            useCash=useCash,
        ),
        conn=conn,
    )


def _get_cash_item(conn: Connection) -> PortfolioItemDTO:
    """Fetch the CASH item (locked for update), creating it with a zero balance if it doesn't exist yet."""
    cash = PortfolioItemRepository.get_by_ticker_and_asset_type(
        CASH_TICKER, CASH_ASSET_TYPE, conn=conn, for_update=True,
    )
    if cash is not None:
        return cash
    return PortfolioItemRepository.add(
        PortfolioItemDTO(ticker=CASH_TICKER, assetType=CASH_ASSET_TYPE, quantity=0, costBasis=0),
        conn=conn,
    )


def _debit_cash(
    amount: float, date: datetime, conn: Connection, useCash: bool, cash: Optional[PortfolioItemDTO] = None,
) -> TransactionDTO:
    """Validate + apply a cash debit. Pass `cash` in if the caller already holds it locked (see `_sell_asset`)."""
    cash = cash or _get_cash_item(conn)
    _validate_debit(cash, amount, date, conn, label='CASH balance', useCash=useCash)

    cash.quantity = round_money(cash.quantity - amount)
    cash.costBasis = round_money(cash.costBasis - amount)  # cash costBasis always mirrors quantity 1:1
    PortfolioItemRepository.update(cash, conn=conn)
    return _record_cash_movement(cash.id, 'sell', amount, date, conn, useCash=useCash)


def _credit_cash(
    amount: float, date: datetime, conn: Connection, useCash: bool, cash: Optional[PortfolioItemDTO] = None,
) -> TransactionDTO:
    """Apply a cash credit - no validation needed, credits can't go negative."""
    cash = cash or _get_cash_item(conn)
    cash.quantity = round_money(cash.quantity + amount)
    cash.costBasis = round_money(cash.costBasis + amount)  # cash costBasis always mirrors quantity 1:1
    PortfolioItemRepository.update(cash, conn=conn)
    return _record_cash_movement(cash.id, 'buy', amount, date, conn, useCash=useCash)


# --- ADD flow (type='buy'): buy stock/bond, or deposit cash --------------------------------

def _add_asset(request: RecordTransactionRequestDTO, date: datetime, conn: Connection) -> TransactionDTO:
    if _is_cash(request):
        return _credit_cash(request.quantity, date, conn, useCash=False)
    return _buy_asset(request, date, conn)


def _buy_asset(request: RecordTransactionRequestDTO, date: datetime, conn: Connection) -> TransactionDTO:
    # 1. validate and debit CASH first, if this purchase is funded from the cashBalance
    if request.useCash:
        cost = round_money(request.quantity * request.price)
        _debit_cash(cost, date, conn, useCash=True)

    # 2. update the existing holding, or create it on the first buy of this ticker. 
    item = PortfolioItemRepository.get_by_ticker_and_asset_type(
        request.ticker, request.assetType, conn=conn, for_update=True,
    )
    is_backdated = item is not None and _is_backdated(item, date, conn)
    if item is None:
        item = PortfolioItemRepository.add(
            PortfolioItemDTO(
                ticker=request.ticker,
                assetType=request.assetType,
                quantity=round_money(request.quantity),
                costBasis=round_money(request.quantity * request.price),
            ),
            conn=conn,
        )   
    elif not is_backdated:
        item.quantity = round_money(item.quantity + request.quantity)
        item.costBasis = round_money(item.costBasis + request.quantity * request.price)
        PortfolioItemRepository.update(item, conn=conn)

    # 3. record the buy transaction itself
    transaction = TransactionRepository.add(
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

    # 4. additional - if transaction is backdated: fold it into the average cost at the point it actually happened, instead of
    # just appending it onto whatever the running total is today
    if is_backdated:
        _recompute_cost_basis_for_backdated_transaction(item, conn)

    return transaction


# --- REMOVE flow (type='sell'): sell stock/bond, or withdraw cash --------------------------

def _remove_asset(request: RecordTransactionRequestDTO, date: datetime, conn: Connection) -> TransactionDTO:
    if _is_cash(request):
        return _debit_cash(request.quantity, date, conn, useCash=False)
    return _sell_asset(request, date, conn)


def _sell_asset(request: RecordTransactionRequestDTO, date: datetime, conn: Connection) -> TransactionDTO:
    # 1. lock CASH before the stock/bond row, same order _buy_asset uses (avoids deadlock)
    cash = _get_cash_item(conn)
    item = PortfolioItemRepository.get_by_ticker_and_asset_type(
        request.ticker, request.assetType, conn=conn, for_update=True,
    )
    if item is None:
        raise PortfolioItemNotFoundError(
            f"No portfolio item found for ticker '{request.ticker}' ({request.assetType})"
        )

    # 2. make sure this sell doesn't drive the holding negative, now or historically
    _validate_debit(item, request.quantity, date, conn, label=f"'{request.ticker}' quantity")
    is_backdated = _is_backdated(item, date, conn)

    # 3. credit the proceeds to CASH
    proceeds = round_money(request.quantity * request.price)
    _credit_cash(proceeds, date, conn, useCash=True, cash=cash)

    # 4. reduce the holding, carrying the average cost basis over to what remains. Skipped when
    # backdated - the replay in step 6 recomputes this correctly instead.
    if not is_backdated:
        cost_basis_per_share = item.costBasis / item.quantity
        new_quantity = round_money(item.quantity - request.quantity)
        item.costBasis = round_money(cost_basis_per_share * new_quantity)
        item.quantity = new_quantity
        PortfolioItemRepository.update(item, conn=conn)

    # 5. record the sell itself
    transaction = TransactionRepository.add(
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

    # 6. additional backdated: fold it into the average cost at the point it actually happened, instead of
    # just appending it onto whatever the running total is today
    if is_backdated:
        _recompute_cost_basis_for_backdated_transaction(item, conn)

    return transaction
