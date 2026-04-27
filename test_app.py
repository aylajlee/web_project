import pytest

from routes import app

def test_index_route():
    client = app.test_client()
    response = client.get('/')
    
    assert response.status_code == 200

# API test
def test_observation_route():
    client = app.test_client()
    response = client.get('/observations')
    assert response.status_code == 200