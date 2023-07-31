import pytest
import requests

from app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_api_call(client):
    payload = {
        "description": "I want to make an app that helps onboard employees to software companies"
    }

    # Use the Flask test client to make the HTTP POST request
    response = client.post('/', json=payload)

    assert response.status_code == 200
    data = response.json
    assert isinstance(data["body"]["recommendations"], list)
