import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app
from models.PerformanceHistoryResultDTO import PerformanceHistoryResultDTO
from models.PerformancePointDTO import PerformancePointDTO


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('routes.performance.PerformanceService.get_performance')
def test_get_performance_returns_history_ranges(mock_get_performance, client):
    mock_get_performance.return_value = PerformanceHistoryResultDTO(
        ranges={
            '1D': [PerformancePointDTO(date='2026-07-31T09:30:00', value=1000.0)],
            '1W': [],
            '1M': [],
            '6M': [],
            '1Y': [],
            'ALL': [PerformancePointDTO(date='2026-07-31', value=1000.0)],
        }
    )

    response = client.get('/api/performance')

    assert response.status_code == 200
    assert response.json == {
        'ranges': {
            '1D': [{'date': '2026-07-31T09:30:00', 'value': 1000.0}],
            '1W': [],
            '1M': [],
            '6M': [],
            '1Y': [],
            'ALL': [{'date': '2026-07-31', 'value': 1000.0}],
        }
    }
    mock_get_performance.assert_called_once_with()


@patch('routes.performance.PerformanceService.get_performance')
def test_get_performance_returns_502_on_failure(mock_get_performance, client):
    mock_get_performance.side_effect = ConnectionError('database unavailable')

    response = client.get('/api/performance')

    assert response.status_code == 502
    assert response.json == {'error': 'Failed to fetch performance history: database unavailable'}
