import os
import sys
import uuid
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from repository.portfolio_item_repository import PortfolioItemRepository


def _mock_conn(mock_get_connection, cursor):
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    mock_get_connection.return_value.__enter__.return_value = conn
    return conn


def _row(**overrides):
    # id is a real uuid.UUID here, matching what psycopg actually returns for a Postgres UUID
    # column — Pydantic won't coerce a UUID object into a str field on its own, so this is what
    # catches that class of bug instead of a plain string literal masking it
    row = {
        'id': uuid.uuid4(), 'ticker': 'AAPL', 'assetType': 'stock',
        'quantity': 10.0, 'costBasis': 1000.0, 'lastUpdated': None,
    }
    row.update(overrides)
    return row


@patch('repository.portfolio_item_repository.get_connection')
def test_get_returns_item_when_found(mock_get_connection):
    cursor = MagicMock()
    row = _row()
    cursor.fetchone.return_value = row
    _mock_conn(mock_get_connection, cursor)

    result = PortfolioItemRepository.get('abc-123')
    assert result.ticker == 'AAPL'
    assert result.id == str(row['id'])


@patch('repository.portfolio_item_repository.get_connection')
def test_get_returns_none_when_not_found(mock_get_connection):
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    _mock_conn(mock_get_connection, cursor)

    assert PortfolioItemRepository.get('missing') is None


@patch('repository.portfolio_item_repository.get_connection')
def test_get_by_ticker_returns_item_when_found(mock_get_connection):
    cursor = MagicMock()
    cursor.fetchone.return_value = _row()
    _mock_conn(mock_get_connection, cursor)

    result = PortfolioItemRepository.get_by_ticker('AAPL')
    assert result.ticker == 'AAPL'


@patch('repository.portfolio_item_repository.get_connection')
def test_list_all_returns_every_row(mock_get_connection):
    cursor = MagicMock()
    cursor.fetchall.return_value = [_row(), _row(ticker='GOOG', id=uuid.uuid4())]
    _mock_conn(mock_get_connection, cursor)

    result = PortfolioItemRepository.list_all()
    assert [item.ticker for item in result] == ['AAPL', 'GOOG']


@patch('repository.portfolio_item_repository.get_connection')
def test_list_all_returns_empty_list_when_no_rows(mock_get_connection):
    cursor = MagicMock()
    cursor.fetchall.return_value = []
    _mock_conn(mock_get_connection, cursor)

    assert PortfolioItemRepository.list_all() == []


@patch('repository.portfolio_item_repository.get_connection')
def test_add_sets_generated_id_and_last_updated(mock_get_connection):
    from models.PortfolioItemDTO import PortfolioItemDTO

    cursor = MagicMock()
    new_id = uuid.uuid4()
    cursor.fetchone.return_value = {'id': new_id}
    _mock_conn(mock_get_connection, cursor)

    item = PortfolioItemDTO(ticker='AAPL', assetType='stock', quantity=10, costBasis=1000)
    result = PortfolioItemRepository.add(item)
    assert result.id == str(new_id)
    assert result.lastUpdated is not None


@patch('repository.portfolio_item_repository.get_connection')
def test_update_executes_update_statement(mock_get_connection):
    from models.PortfolioItemDTO import PortfolioItemDTO

    cursor = MagicMock()
    _mock_conn(mock_get_connection, cursor)

    item = PortfolioItemDTO(id=str(uuid.uuid4()), ticker='AAPL', assetType='stock', quantity=15, costBasis=1500)
    PortfolioItemRepository.update(item)
    assert cursor.execute.call_count == 1
    assert 'UPDATE' in cursor.execute.call_args[0][0]


@patch('repository.portfolio_item_repository.get_connection')
def test_delete_executes_delete_statement(mock_get_connection):
    cursor = MagicMock()
    _mock_conn(mock_get_connection, cursor)

    PortfolioItemRepository.delete('abc-123')
    assert cursor.execute.call_count == 1
    assert 'DELETE' in cursor.execute.call_args[0][0]
