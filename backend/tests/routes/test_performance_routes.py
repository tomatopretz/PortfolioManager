import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app
from models.PerformanceSummaryResultDTO import PerformanceSummaryResultDTO


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('routes.performance.PerformanceService.get_performance')
def test_get_performance_returns_summary(mock_get_performance, client):
    mock_get_performance.return_value = PerformanceSummaryResultDTO(
        totalValue=1500.0,
        totalCostBasis=1000.0,
        totalPnL=500.0,
        totalPnLPercent=50.0,
        cashBalance=0.0,
        allocation=[],
    )

    response = client.get('/api/performance')

    assert response.status_code == 200
    assert response.json == {
        'totalValue': 1500.0,
        'totalCostBasis': 1000.0,
        'totalPnL': 500.0,
        'totalPnLPercent': 50.0,
        'cashBalance': 0.0,
        'allocation': [],
    }
    mock_get_performance.assert_called_once_with()


@patch('routes.performance.PerformanceService.get_performance')
def test_get_performance_returns_502_on_failure(mock_get_performance, client):
    mock_get_performance.side_effect = ConnectionError('database unavailable')

    response = client.get('/api/performance')

    assert response.status_code == 502
    assert response.json == {'error': 'Failed to fetch performance: database unavailable'}
