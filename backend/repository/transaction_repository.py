from datetime import datetime
from typing import Optional

from psycopg import Connection

from db import get_cursor
from models.TransactionDTO import TransactionDTO
from models.RecordTransactionRequestDTO import CASH_ASSET_TYPE

TABLE = 'transaction'
_COLUMNS = (
    'id, portfolio_item_id AS "portfolioItemId", type, quantity, price, date, '
    'use_cash AS "useCash"'
)
# table-prefixed variant for queries that join against portfolio_item (both tables have an `id` column)
_JOIN_COLUMNS = (
    't.id, t.portfolio_item_id AS "portfolioItemId", t.type, t.quantity, t.price, t.date, '
    't.use_cash AS "useCash"'
)


def _row_to_transaction(row: dict) -> TransactionDTO:
    # column aliases already match TransactionDTO's field names exactly; id and portfolioItemId
    # still need an explicit str() since psycopg returns Postgres UUID columns as uuid.UUID, and
    # Pydantic won't coerce that into a str field on its own
    return TransactionDTO(**{**row, 'id': str(row['id']), 'portfolioItemId': str(row['portfolioItemId'])})


class TransactionRepository:
    """CRUD access to the Transaction table."""

    @staticmethod
    def get(transaction_id: str) -> Optional[TransactionDTO]:
        with get_cursor() as cur:
            cur.execute(f'SELECT {_COLUMNS} FROM {TABLE} WHERE id = %s', (transaction_id,))
            row = cur.fetchone()
            return _row_to_transaction(row) if row else None

    @staticmethod
    def list_all() -> list[TransactionDTO]:
        with get_cursor() as cur:
            cur.execute(f'SELECT {_COLUMNS} FROM {TABLE} ORDER BY date DESC')
            return [_row_to_transaction(row) for row in cur.fetchall()]

    @staticmethod
    def list_by_portfolio_item(portfolio_item_id: str, conn: Optional[Connection] = None) -> list[TransactionDTO]:
        with get_cursor(conn) as cur:
            cur.execute(
                f'SELECT {_COLUMNS} FROM {TABLE} WHERE portfolio_item_id = %s ORDER BY date',
                (portfolio_item_id,),
            )
            return [_row_to_transaction(row) for row in cur.fetchall()]

    @staticmethod
    def get_latest_date(portfolio_item_id: str, conn: Optional[Connection] = None) -> Optional[datetime]:
        """Latest transaction date on record for one item - a cheap indexed MAX() instead of
        fetching the whole history"""
        with get_cursor(conn) as cur:
            cur.execute(f'SELECT MAX(date) AS date FROM {TABLE} WHERE portfolio_item_id = %s', (portfolio_item_id,))
            return cur.fetchone()['date']

    @staticmethod
    def list_by_tickers(tickers: list[str]) -> list[TransactionDTO]:
        with get_cursor() as cur:
            cur.execute(
                f'SELECT {_JOIN_COLUMNS} FROM {TABLE} t '
                f'JOIN portfolio_item p ON p.id = t.portfolio_item_id '
                f'WHERE p.ticker = ANY(%s) ORDER BY t.date DESC',
                (tickers,),
            )
            return [_row_to_transaction(row) for row in cur.fetchall()]

    @staticmethod
    def list_export_rows() -> list[dict]:
        """Return transaction rows joined to ticker/type for CSV export."""
        with get_cursor() as cur:
            cur.execute(
                f'SELECT t.type, t.quantity, t.price, t.date, t.use_cash AS "useCash", '
                f'p.ticker, p.asset_type AS "assetType" '
                f'FROM {TABLE} t '
                f'JOIN portfolio_item p ON p.id = t.portfolio_item_id '
                f'WHERE NOT (p.asset_type = %s AND t.use_cash = TRUE) '
                f'ORDER BY t.date ASC, t.id ASC',
                (CASH_ASSET_TYPE,),
            )
            return cur.fetchall()

    @staticmethod
    def add(transaction: TransactionDTO, conn: Optional[Connection] = None) -> TransactionDTO:
        with get_cursor(conn) as cur:
            cur.execute(
                f'INSERT INTO {TABLE} (portfolio_item_id, type, quantity, price, date, use_cash) '
                f'VALUES (%s, %s, %s, %s, %s, %s) RETURNING id',
                (
                    transaction.portfolioItemId,
                    transaction.type,
                    transaction.quantity,
                    transaction.price,
                    transaction.date,
                    transaction.useCash,
                ),
            )
            transaction.id = str(cur.fetchone()['id'])
        return transaction
