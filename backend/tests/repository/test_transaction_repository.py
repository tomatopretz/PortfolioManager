import os
import sys
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from repository.transaction_repository import TransactionRepository


def _mock_conn(mock_get_connection, cursor):
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    mock_get_connection.return_value.__enter__.return_value = conn
    return conn


def _row(**overrides):
    # id/portfolioItemId are real uuid.UUID here, matching what psycopg actually returns for a
    # Postgres UUID column — Pydantic won't coerce a UUID object into a str field on its own, so
    # this is what catches that class of bug instead of a plain string literal masking it
    row = {
        'id': uuid.uuid4(), 'portfolioItemId': uuid.uuid4(), 'type': 'buy',
        'quantity': 10.0, 'price': 100.0, 'date': datetime(2026, 7, 20), 'useCash': True,
    }
    row.update(overrides)
    return row


@patch('repository.transaction_repository.get_connection')
def test_get_returns_transaction_when_found(mock_get_connection):
    cursor = MagicMock()
    row = _row()
    cursor.fetchone.return_value = row
    _mock_conn(mock_get_connection, cursor)

    result = TransactionRepository.get('txn-1')
    assert result.type == 'buy'
    assert result.portfolioItemId == str(row['portfolioItemId'])


@patch('repository.transaction_repository.get_connection')
def test_get_returns_none_when_not_found(mock_get_connection):
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    _mock_conn(mock_get_connection, cursor)

    assert TransactionRepository.get('missing') is None


@patch('repository.transaction_repository.get_connection')
def test_list_all_returns_every_row(mock_get_connection):
    cursor = MagicMock()
    row1, row2 = _row(), _row(id=uuid.uuid4(), type='sell')
    cursor.fetchall.return_value = [row1, row2]
    _mock_conn(mock_get_connection, cursor)

    result = TransactionRepository.list_all()
    assert [t.id for t in result] == [str(row1['id']), str(row2['id'])]


@patch('repository.transaction_repository.get_connection')
def test_list_by_portfolio_item_filters_correctly(mock_get_connection):
    cursor = MagicMock()
    cursor.fetchall.return_value = [_row()]
    _mock_conn(mock_get_connection, cursor)

    result = TransactionRepository.list_by_portfolio_item('item-1')
    assert len(result) == 1
    assert 'portfolio_item_id = %s' in cursor.execute.call_args[0][0]
    assert cursor.execute.call_args[0][1] == ('item-1',)


@patch('repository.transaction_repository.get_connection')
def test_add_sets_generated_id(mock_get_connection):
    from models.TransactionDTO import TransactionDTO

    cursor = MagicMock()
    new_id = uuid.uuid4()
    cursor.fetchone.return_value = {'id': new_id}
    _mock_conn(mock_get_connection, cursor)

    transaction = TransactionDTO(
        portfolioItemId=str(uuid.uuid4()), type='buy', quantity=10, price=100,
        date=datetime(2026, 7, 20), useCash=True,
    )
    result = TransactionRepository.add(transaction)
    assert result.id == str(new_id)


@patch('repository.transaction_repository.get_connection')
def test_update_executes_update_statement(mock_get_connection):
    from models.TransactionDTO import TransactionDTO

    cursor = MagicMock()
    _mock_conn(mock_get_connection, cursor)

    transaction = TransactionDTO(
        id=str(uuid.uuid4()), portfolioItemId=str(uuid.uuid4()), type='sell', quantity=5, price=110,
        date=datetime(2026, 7, 21), useCash=True,
    )
    TransactionRepository.update(transaction)
    assert cursor.execute.call_count == 1
    assert 'UPDATE' in cursor.execute.call_args[0][0]


@patch('repository.transaction_repository.get_connection')
def test_delete_executes_delete_statement(mock_get_connection):
    cursor = MagicMock()
    cursor.rowcount = 1
    _mock_conn(mock_get_connection, cursor)

    assert TransactionRepository.delete('txn-1') is True
    assert cursor.execute.call_count == 1
    assert 'DELETE' in cursor.execute.call_args[0][0]


@patch('repository.transaction_repository.get_connection')
def test_delete_returns_false_when_no_row_matched(mock_get_connection):
    cursor = MagicMock()
    cursor.rowcount = 0
    _mock_conn(mock_get_connection, cursor)

    assert TransactionRepository.delete('txn-1') is False
