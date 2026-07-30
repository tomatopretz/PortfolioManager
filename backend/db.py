import os
from contextlib import contextmanager
from typing import ContextManager, Iterator, Optional

import psycopg
from dotenv import load_dotenv
from psycopg import Connection
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
