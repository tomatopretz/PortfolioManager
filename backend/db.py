import os
from contextlib import contextmanager
from typing import ContextManager, Iterator, Optional

import psycopg
from dotenv import load_dotenv
from psycopg import Connection, Cursor
from psycopg.rows import dict_row

load_dotenv()


class DatabaseConfigError(RuntimeError):
    """Raised when the backend database connection is not configured."""


class Database:
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url

    def _database_url(self) -> str:
        database_url = self.database_url or os.getenv("DATABASE_URL")
        if not database_url:
            raise DatabaseConfigError("DATABASE_URL is not set")
        return database_url

    @contextmanager
    def connection(self) -> Iterator[Connection]:
        with psycopg.connect(self._database_url(), row_factory=dict_row) as conn:
            yield conn

    @contextmanager
    def transaction(self) -> Iterator[Connection]:
        with self.connection() as conn:
            with conn.transaction():
                yield conn


db = Database()


def get_connection() -> ContextManager[Connection]:
    return db.connection()


def get_transaction() -> ContextManager[Connection]:
    return db.transaction()


@contextmanager
def get_cursor(conn: Optional[Connection] = None) -> Iterator[Cursor]:
    """Yield a cursor. If `conn` is given (e.g. from get_transaction()), reuses it so the
    caller controls commit/rollback across multiple calls; otherwise opens its own
    self-contained, auto-committing connection."""
    if conn is not None:
        # Caller (e.g. PortfolioService, inside a `with get_transaction() as conn:` block)
        # already owns a connection spanning several repo calls. Just hand back a cursor on
        # that same connection - don't commit/close here, the caller's `with` block does that
        # once ALL steps succeed (or rolls everything back together if one of them raises).
        with conn.cursor() as cur:
            yield cur
        return

    # No shared connection was passed in - this is a single, self-contained call (the common
    # case for most repo methods). Open our own connection just for this one operation; when
    # the `with` block below exits, get_connection()'s own context manager commits (or rolls
    # back on exception) and closes it automatically.
    with get_connection() as owned_conn, owned_conn.cursor() as cur:
        yield cur
