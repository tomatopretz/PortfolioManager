import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_get_portfolio_endpoint_exists(client):
    response = client.get('/api/portfolio')
    assert response.status_code == 501

def test_get_portfolio_items_endpoint_exists(client):
    response = client.get('/api/portfolio/items')
    assert response.status_code == 501
