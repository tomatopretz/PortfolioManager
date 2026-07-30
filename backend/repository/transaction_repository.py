from typing import Optional

from db import get_connection
from models.TransactionDTO import TransactionDTO

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
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(f'SELECT {_COLUMNS} FROM {TABLE} WHERE id = %s', (transaction_id,))
            row = cur.fetchone()
            return _row_to_transaction(row) if row else None

    @staticmethod
    def list_all() -> list[TransactionDTO]:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(f'SELECT {_COLUMNS} FROM {TABLE} ORDER BY date DESC')
            return [_row_to_transaction(row) for row in cur.fetchall()]

    @staticmethod
    def list_by_portfolio_item(portfolio_item_id: str) -> list[TransactionDTO]:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                f'SELECT {_COLUMNS} FROM {TABLE} WHERE portfolio_item_id = %s ORDER BY date DESC',
                (portfolio_item_id,),
            )
            return [_row_to_transaction(row) for row in cur.fetchall()]

    @staticmethod
    def list_by_tickers(tickers: list[str]) -> list[TransactionDTO]:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                f'SELECT {_JOIN_COLUMNS} FROM {TABLE} t '
                f'JOIN portfolio_item p ON p.id = t.portfolio_item_id '
                f'WHERE p.ticker = ANY(%s) ORDER BY t.date DESC',
                (tickers,),
            )
            return [_row_to_transaction(row) for row in cur.fetchall()]

    @staticmethod
    def add(transaction: TransactionDTO) -> TransactionDTO:
        with get_connection() as conn, conn.cursor() as cur:
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

    @staticmethod
    def update(transaction: TransactionDTO) -> TransactionDTO:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                f'UPDATE {TABLE} SET portfolio_item_id = %s, type = %s, quantity = %s, '
                f'price = %s, date = %s, use_cash = %s WHERE id = %s',
                (
                    transaction.portfolioItemId,
                    transaction.type,
                    transaction.quantity,
                    transaction.price,
                    transaction.date,
                    transaction.useCash,
                    transaction.id,
                ),
            )
        return transaction

    @staticmethod
    def delete(transaction_id: str) -> bool:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(f'DELETE FROM {TABLE} WHERE id = %s', (transaction_id,))
            return cur.rowcount > 0
