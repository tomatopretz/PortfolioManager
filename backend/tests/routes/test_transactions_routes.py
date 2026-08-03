import os
import sys
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app
from models.TransactionDTO import TransactionDTO
from services.transaction_service import InsufficientCashError, InsufficientQuantityError, PortfolioItemNotFoundError


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def _transaction(**overrides):
    defaults = dict(
        id='11111111-1111-1111-1111-111111111111',
        portfolioItemId='22222222-2222-2222-2222-222222222222',
        type='buy', quantity=10, price=150, date=datetime(2026, 7, 31, tzinfo=timezone.utc), useCash=True,
    )
    defaults.update(overrides)
    return TransactionDTO(**defaults)


def _buy_body(**overrides):
    body = dict(type='buy', ticker='AAPL', assetType='stock', quantity=10, price=150, useCash=True)
    body.update(overrides)
    return body


# --- GET /api/transactions ----------------------------------------------------------------------

@patch('routes.transactions.TransactionService.list_transactions')
def test_get_transactions_returns_all_when_no_filter(mock_list_transactions, client):
    mock_list_transactions.return_value = [_transaction()]
    response = client.get('/api/transactions')
    assert response.status_code == 200
    assert len(response.json) == 1
    mock_list_transactions.assert_called_once_with(None)


@patch('routes.transactions.TransactionService.list_transactions')
def test_get_transactions_filters_by_tickers_case_insensitively(mock_list_transactions, client):
    mock_list_transactions.return_value = []
    client.get('/api/transactions?tickers=aapl,goog')
    mock_list_transactions.assert_called_once_with(['AAPL', 'GOOG'])


@patch('routes.transactions.TransactionService.list_transactions')
def test_get_transactions_returns_502_on_failure(mock_list_transactions, client):
    mock_list_transactions.side_effect = ConnectionError('DB unreachable')
    response = client.get('/api/transactions')
    assert response.status_code == 502


# --- POST /api/transactions ---------------------------------------------------------------------

@patch('routes.transactions.TransactionService.record_transaction')
def test_record_transaction_returns_201_on_success(mock_record_transaction, client):
    mock_record_transaction.return_value = _transaction()
    response = client.post('/api/transactions', json=_buy_body())
    assert response.status_code == 201
    assert response.json['type'] == 'buy'
    assert response.json['quantity'] == 10


@patch('routes.transactions.TransactionService.record_transaction')
def test_record_transaction_normalizes_ticker_and_asset_type_case(mock_record_transaction, client):
    mock_record_transaction.return_value = _transaction()
    client.post('/api/transactions', json=_buy_body(ticker='aapl', assetType='stock'))

    [sent_request], _ = mock_record_transaction.call_args
    assert sent_request.ticker == 'AAPL'
    assert sent_request.assetType == 'STOCK'


@patch('routes.transactions.TransactionService.record_transaction')
def test_record_transaction_omits_date_by_default(mock_record_transaction, client):
    mock_record_transaction.return_value = _transaction()
    client.post('/api/transactions', json=_buy_body())

    [sent_request], _ = mock_record_transaction.call_args
    assert sent_request.date is None  # service layer defaults it to now() when not supplied


@patch('routes.transactions.TransactionService.record_transaction')
def test_record_transaction_passes_through_client_supplied_date(mock_record_transaction, client):
    mock_record_transaction.return_value = _transaction()
    client.post('/api/transactions', json=_buy_body(date='2026-01-01T00:00:00Z'))

    [sent_request], _ = mock_record_transaction.call_args
    assert sent_request.date == datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_record_transaction_rejects_missing_required_fields(client):
    response = client.post('/api/transactions', json={'type': 'buy'})
    assert response.status_code == 422
    assert 'ticker' in response.json['error']


def test_record_transaction_rejects_missing_price_for_non_cash(client):
    response = client.post('/api/transactions', json=_buy_body(price=None))
    assert response.status_code == 422


def test_record_transaction_rejects_cash_asset_type_with_non_usd_ticker(client):
    # assetType=CASH routes straight to the deposit/withdraw flow, which only ever touches the
    # USD balance - a mismatched ticker here would otherwise be silently ignored
    response = client.post('/api/transactions', json=_buy_body(assetType='cash', ticker='MU', price=None))
    assert response.status_code == 422


def test_record_transaction_rejects_usd_ticker_with_non_cash_asset_type(client):
    response = client.post('/api/transactions', json=_buy_body(ticker='usd', assetType='stock'))
    assert response.status_code == 422


def test_record_transaction_rejects_fractional_quantity_for_non_cash(client):
    response = client.post('/api/transactions', json=_buy_body(quantity=1.5))
    assert response.status_code == 422


@patch('routes.transactions.TransactionService.record_transaction')
def test_record_transaction_allows_fractional_quantity_for_cash(mock_record_transaction, client):
    mock_record_transaction.return_value = _transaction()
    response = client.post(
        '/api/transactions', json=_buy_body(ticker='usd', assetType='cash', price=None, quantity=12.34),
    )
    assert response.status_code == 201


@patch('routes.transactions.TransactionService.record_transaction')
def test_record_transaction_returns_404_when_item_not_found(mock_record_transaction, client):
    mock_record_transaction.side_effect = PortfolioItemNotFoundError("No portfolio item found for ticker 'AAPL'")
    response = client.post('/api/transactions', json=_buy_body(type='sell'))
    assert response.status_code == 404
    assert 'AAPL' in response.json['error']


@patch('routes.transactions.TransactionService.record_transaction')
def test_record_transaction_returns_422_on_insufficient_cash(mock_record_transaction, client):
    mock_record_transaction.side_effect = InsufficientCashError('CASH balance 100 is less than purchase cost 1500')
    response = client.post('/api/transactions', json=_buy_body())
    assert response.status_code == 422


@patch('routes.transactions.TransactionService.record_transaction')
def test_record_transaction_returns_422_on_insufficient_quantity(mock_record_transaction, client):
    mock_record_transaction.side_effect = InsufficientQuantityError("Cannot sell 100 of 'AAPL': only 5 held")
    response = client.post('/api/transactions', json=_buy_body(type='sell'))
    assert response.status_code == 422


@patch('routes.transactions.TransactionService.record_transaction')
def test_record_transaction_returns_502_on_unexpected_error(mock_record_transaction, client):
    mock_record_transaction.side_effect = ConnectionError('DB unreachable')
    response = client.post('/api/transactions', json=_buy_body())
    assert response.status_code == 502


def test_transactions_does_not_accept_delete(client):
    # transactions are immutable once recorded - no reversal/delete endpoint by design
    response = client.delete(f'/api/transactions/{uuid.uuid4()}')
    assert response.status_code == 404
