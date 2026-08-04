import os
import sys
import uuid
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from repository.portfolio_item_repository import PortfolioItemRepository


def _mock_cursor(mock_get_cursor, cursor):
    # makes `with get_cursor() as cur:` inside the repository yield our fake cursor instead of a real DB one
    mock_get_cursor.return_value.__enter__.return_value = cursor


def _row(**overrides):
    # id is a real uuid.UUID here, matching what psycopg actually returns for a Postgres UUID
    row = {
        'id': uuid.uuid4(), 'ticker': 'AAPL', 'assetType': 'stock',
        'quantity': 10.0, 'costBasis': 1000.0, 'lastUpdated': None,
    }
    row.update(overrides)
    return row


@patch('repository.portfolio_item_repository.get_cursor')  # mock: replace get_cursor so no real DB call happens
def test_get_returns_item_when_found(mock_get_cursor):
    # Given a cursor that returns one matching row
    cursor = MagicMock()
    row = _row()
    cursor.fetchone.return_value = row
    _mock_cursor(mock_get_cursor, cursor)

    # When fetching a portfolio item by id
    result = PortfolioItemRepository.get('abc-123')
    # Then the DTO returned reflects that row's data
    assert result.ticker == 'AAPL'
    assert result.id == str(row['id'])


@patch('repository.portfolio_item_repository.get_cursor')  # mock: replace get_cursor so no real DB call happens
def test_get_returns_none_when_not_found(mock_get_cursor):
    # Given a cursor that finds no matching row
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    _mock_cursor(mock_get_cursor, cursor)

    # When/Then fetching a portfolio item by id returns None instead of raising
    assert PortfolioItemRepository.get('missing') is None


@patch('repository.portfolio_item_repository.get_cursor')  # mock: replace get_cursor so no real DB call happens
def test_list_all_returns_every_row(mock_get_cursor):
    # Given a cursor that returns two rows
    cursor = MagicMock()
    cursor.fetchall.return_value = [_row(), _row(ticker='GOOG', id=uuid.uuid4())]
    _mock_cursor(mock_get_cursor, cursor)

    # When listing all portfolio items
    result = PortfolioItemRepository.list_all()
    # Then every row comes back as a DTO, in order
    assert [item.ticker for item in result] == ['AAPL', 'GOOG']


@patch('repository.portfolio_item_repository.get_cursor')  # mock: replace get_cursor so no real DB call happens
def test_list_all_returns_empty_list_when_no_rows(mock_get_cursor):
    # Given a cursor that returns no rows
    cursor = MagicMock()
    cursor.fetchall.return_value = []
    _mock_cursor(mock_get_cursor, cursor)

    # When/Then listing all portfolio items returns [] rather than None or an error
    assert PortfolioItemRepository.list_all() == []


@patch('repository.portfolio_item_repository.get_cursor')  # mock: replace get_cursor so no real DB call happens
def test_add_sets_generated_id_and_last_updated(mock_get_cursor):
    from models.PortfolioItemDTO import PortfolioItemDTO

    # Given a cursor that returns the id the DB would generate on insert
    cursor = MagicMock()
    new_id = uuid.uuid4()
    cursor.fetchone.return_value = {'id': new_id}
    _mock_cursor(mock_get_cursor, cursor)

    # When adding a new portfolio item (no id set yet)
    item = PortfolioItemDTO(ticker='AAPL', assetType='stock', quantity=10, costBasis=1000)
    result = PortfolioItemRepository.add(item)
    # Then the returned DTO is filled in with the DB-generated id and a lastUpdated timestamp
    assert result.id == str(new_id)
    assert result.lastUpdated is not None


@patch('repository.portfolio_item_repository.get_cursor')  # mock: replace get_cursor so no real DB call happens
def test_set_favourite_executes_update_statement_with_only_favourite_and_timestamp(mock_get_cursor):
    # Given a cursor standing in for the DB connection
    cursor = MagicMock()
    _mock_cursor(mock_get_cursor, cursor)

    # When toggling isFavourite on an item
    PortfolioItemRepository.set_favourite('abc-123', True)

    # Then exactly one UPDATE ran, touching only is_favourite + lastUpdated (not quantity/cost_basis)
    assert cursor.execute.call_count == 1
    sql, params = cursor.execute.call_args[0]
    assert 'UPDATE' in sql
    assert 'is_favourite' in sql
    # deliberately doesn't touch quantity/cost_basis - only isFavourite + lastUpdated + the id
    assert 'quantity' not in sql
    assert 'cost_basis' not in sql
    assert params == (True, params[1], 'abc-123')


@patch('repository.portfolio_item_repository.get_cursor')  # mock: replace get_cursor so no real DB call happens
def test_update_executes_update_statement(mock_get_cursor):
    from models.PortfolioItemDTO import PortfolioItemDTO

    # Given an existing portfolio item with changed values
    cursor = MagicMock()
    _mock_cursor(mock_get_cursor, cursor)

    # When updating it
    item = PortfolioItemDTO(id=str(uuid.uuid4()), ticker='AAPL', assetType='stock', quantity=15, costBasis=1500)
    PortfolioItemRepository.update(item)
    # Then exactly one UPDATE statement was executed
    assert cursor.execute.call_count == 1
    assert 'UPDATE' in cursor.execute.call_args[0][0]


