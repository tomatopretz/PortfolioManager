import os
import sys
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from repository.transaction_repository import TransactionRepository


def _mock_cursor(mock_get_cursor, cursor):
    # makes `with get_cursor() as cur:` inside the repository yield our fake cursor instead of a real DB one
    mock_get_cursor.return_value.__enter__.return_value = cursor


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


@patch('repository.transaction_repository.get_cursor')  # mock: replace get_cursor so no real DB call happens
def test_get_returns_transaction_when_found(mock_get_cursor):
    # Given a cursor that returns one matching row
    cursor = MagicMock()
    row = _row()
    cursor.fetchone.return_value = row
    _mock_cursor(mock_get_cursor, cursor)

    # When fetching a transaction by id
    result = TransactionRepository.get('txn-1')
    # Then the DTO returned reflects that row's data
    assert result.type == 'buy'
    assert result.portfolioItemId == str(row['portfolioItemId'])


@patch('repository.transaction_repository.get_cursor')  # mock: replace get_cursor so no real DB call happens
def test_get_returns_none_when_not_found(mock_get_cursor):
    # Given a cursor that finds no matching row
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    _mock_cursor(mock_get_cursor, cursor)

    # When/Then fetching a transaction by id returns None instead of raising
    assert TransactionRepository.get('missing') is None


@patch('repository.transaction_repository.get_cursor')  # mock: replace get_cursor so no real DB call happens
def test_list_all_returns_every_row(mock_get_cursor):
    # Given a cursor that returns two rows
    cursor = MagicMock()
    row1, row2 = _row(), _row(id=uuid.uuid4(), type='sell')
    cursor.fetchall.return_value = [row1, row2]
    _mock_cursor(mock_get_cursor, cursor)

    # When listing all transactions
    result = TransactionRepository.list_all()
    # Then every row comes back as a DTO, in order
    assert [t.id for t in result] == [str(row1['id']), str(row2['id'])]


@patch('repository.transaction_repository.get_cursor')  # mock: replace get_cursor so no real DB call happens
def test_list_by_portfolio_item_returns_matching_rows_in_date_order(mock_get_cursor):
    # Given a cursor that returns two rows for one portfolio item
    cursor = MagicMock()
    item_id = uuid.uuid4()
    row1, row2 = _row(portfolioItemId=item_id), _row(portfolioItemId=item_id, id=uuid.uuid4(), type='sell')
    cursor.fetchall.return_value = [row1, row2]
    _mock_cursor(mock_get_cursor, cursor)

    # When listing that item's transactions
    result = TransactionRepository.list_by_portfolio_item(str(item_id))
    # Then every row comes back as a DTO, in the order the query returned them
    assert [t.id for t in result] == [str(row1['id']), str(row2['id'])]


@patch('repository.transaction_repository.get_cursor')  # mock: replace get_cursor so no real DB call happens
def test_get_latest_date_returns_max_date(mock_get_cursor):
    # Given a cursor that returns the MAX(date) aggregate
    cursor = MagicMock()
    latest = datetime(2026, 7, 20)
    cursor.fetchone.return_value = {'date': latest}
    _mock_cursor(mock_get_cursor, cursor)

    # When/Then fetching the latest date for an item returns it
    assert TransactionRepository.get_latest_date('item-1') == latest


@patch('repository.transaction_repository.get_cursor')  # mock: replace get_cursor so no real DB call happens
def test_get_latest_date_returns_none_when_no_transactions(mock_get_cursor):
    # Given a cursor that returns no aggregate row (no transactions for that item)
    cursor = MagicMock()
    cursor.fetchone.return_value = {'date': None}
    _mock_cursor(mock_get_cursor, cursor)

    # When/Then fetching the latest date for an item with no history returns None
    assert TransactionRepository.get_latest_date('item-1') is None


@patch('repository.transaction_repository.get_cursor')  # mock: replace get_cursor so no real DB call happens
def test_add_sets_generated_id(mock_get_cursor):
    from models.TransactionDTO import TransactionDTO

    # Given a cursor that returns the id the DB would generate on insert
    cursor = MagicMock()
    new_id = uuid.uuid4()
    cursor.fetchone.return_value = {'id': new_id}
    _mock_cursor(mock_get_cursor, cursor)

    # When adding a new transaction (no id set yet)
    transaction = TransactionDTO(
        portfolioItemId=str(uuid.uuid4()), type='buy', quantity=10, price=100,
        date=datetime(2026, 7, 20), useCash=True,
    )
    result = TransactionRepository.add(transaction)
    # Then the returned DTO is filled in with the DB-generated id
    assert result.id == str(new_id)
