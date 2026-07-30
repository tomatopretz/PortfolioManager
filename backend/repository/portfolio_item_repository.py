<<<<<<< HEAD
from datetime import datetime, timezone
from typing import Optional

from db import get_connection
from models.PortfolioItemDTO import PortfolioItemDTO

TABLE = 'portfolio_item'
_COLUMNS = (
    'id, ticker, asset_type AS "assetType", quantity, '
    'cost_basis AS "costBasis", last_updated AS "lastUpdated"'
)


def _row_to_item(row: dict) -> PortfolioItemDTO:
    # column aliases already match PortfolioItemDTO's field names exactly; id still needs an
    # explicit str() since psycopg returns Postgres UUID columns as uuid.UUID, and Pydantic
    # won't coerce that into a str field on its own
    return PortfolioItemDTO(**{**row, 'id': str(row['id'])})


class PortfolioItemRepository:
    """CRUD access to the PortfolioItem table."""

    @staticmethod
    def get(item_id: str) -> Optional[PortfolioItemDTO]:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(f'SELECT {_COLUMNS} FROM {TABLE} WHERE id = %s', (item_id,))
            row = cur.fetchone()
            return _row_to_item(row) if row else None

    @staticmethod
    def get_by_ticker(ticker: str) -> Optional[PortfolioItemDTO]:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(f'SELECT {_COLUMNS} FROM {TABLE} WHERE ticker = %s', (ticker,))
            row = cur.fetchone()
            return _row_to_item(row) if row else None

    @staticmethod
    def list_all() -> list[PortfolioItemDTO]:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(f'SELECT {_COLUMNS} FROM {TABLE} ORDER BY ticker')
            return [_row_to_item(row) for row in cur.fetchall()]

    @staticmethod
    def add(item: PortfolioItemDTO) -> PortfolioItemDTO:
        now = datetime.now(timezone.utc)
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                f'INSERT INTO {TABLE} (ticker, asset_type, quantity, cost_basis, last_updated) '
                f'VALUES (%s, %s, %s, %s, %s) RETURNING id',
                (item.ticker, item.assetType, item.quantity, item.costBasis, now),
            )
            item.id = str(cur.fetchone()['id'])
        item.lastUpdated = now
        return item

    @staticmethod
    def update(item: PortfolioItemDTO) -> PortfolioItemDTO:
        now = datetime.now(timezone.utc)
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                f'UPDATE {TABLE} SET ticker = %s, asset_type = %s, quantity = %s, '
                f'cost_basis = %s, last_updated = %s WHERE id = %s',
                (item.ticker, item.assetType, item.quantity, item.costBasis, now, item.id),
            )
        item.lastUpdated = now
        return item

    @staticmethod
    def delete(item_id: str) -> None:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(f'DELETE FROM {TABLE} WHERE id = %s', (item_id,))
=======
from datetime import datetime, timezone
from typing import Optional

from db import get_connection
from models.PortfolioItemDTO import PortfolioItemDTO

TABLE = 'portfolio_item'
_COLUMNS = (
    'id, ticker, asset_type AS "assetType", quantity, '
    'cost_basis AS "costBasis", is_favourite AS "isFavourite", last_updated AS "lastUpdated"'
)


def _row_to_item(row: dict) -> PortfolioItemDTO:
    # column aliases already match PortfolioItemDTO's field names exactly; id still needs an
    # explicit str() since psycopg returns Postgres UUID columns as uuid.UUID, and Pydantic
    # won't coerce that into a str field on its own
    return PortfolioItemDTO(**{**row, 'id': str(row['id'])})


class PortfolioItemRepository:
    """CRUD access to the PortfolioItem table."""

    @staticmethod
    def get(item_id: str) -> Optional[PortfolioItemDTO]:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(f'SELECT {_COLUMNS} FROM {TABLE} WHERE id = %s', (item_id,))
            row = cur.fetchone()
            return _row_to_item(row) if row else None

    @staticmethod
    def get_by_ticker(ticker: str) -> Optional[PortfolioItemDTO]:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(f'SELECT {_COLUMNS} FROM {TABLE} WHERE ticker = %s', (ticker,))
            row = cur.fetchone()
            return _row_to_item(row) if row else None

    @staticmethod
    def list_all() -> list[PortfolioItemDTO]:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(f'SELECT {_COLUMNS} FROM {TABLE} ORDER BY ticker')
            return [_row_to_item(row) for row in cur.fetchall()]

    @staticmethod
    def add(item: PortfolioItemDTO) -> PortfolioItemDTO:
        now = datetime.now(timezone.utc)
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                f'INSERT INTO {TABLE} (ticker, asset_type, quantity, cost_basis, is_favourite, last_updated) '
                f'VALUES (%s, %s, %s, %s, %s, %s) RETURNING id',
                (item.ticker, item.assetType, item.quantity, item.costBasis, item.isFavourite, now),
            )
            item.id = str(cur.fetchone()['id'])
        item.lastUpdated = now
        return item

    @staticmethod
    def update(item: PortfolioItemDTO) -> PortfolioItemDTO:
        now = datetime.now(timezone.utc)
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                f'UPDATE {TABLE} SET ticker = %s, asset_type = %s, quantity = %s, '
                f'cost_basis = %s, is_favourite = %s, last_updated = %s WHERE id = %s',
                (item.ticker, item.assetType, item.quantity, item.costBasis, item.isFavourite, now, item.id),
            )
        item.lastUpdated = now
        return item

    @staticmethod
    def delete(item_id: str) -> None:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(f'DELETE FROM {TABLE} WHERE id = %s', (item_id,))
>>>>>>> main
