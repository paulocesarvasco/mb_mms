from http import HTTPStatus
import pytest
from flask import Flask

from mb_mms.api.routes import currency_bp
from mb_mms.services.mb_api.mb_api import MB_API
from unittest.mock import patch, MagicMock

@pytest.fixture
def app():
    # Create a Flask app for testing
    app = Flask(__name__)
    app.register_blueprint(currency_bp)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    # Create a test client for the Flask app
    return app.test_client()

def test_root_route(client):
    # Test the root route
    response = client.get('/v1/')
    assert response.status_code == 200
    assert b'Currency MMS initial page!' in response.data

def test_search_route_success(client):
    # Mock the MB_API class and its search_mms method
    with patch('mb_mms.services.mb_api.mb_api.MB_API') as mock_mb_api:
        mock_mb_instance = MagicMock(spec=MB_API)
        mock_mb_api.return_value = mock_mb_instance

        # Mock the search_mms method to return a list of results
        mock_mb_instance.search_mms.return_value = [
            {'timestamp': 1638316800, 'mms': 1.23},
            {'timestamp': 1638403200, 'mms': 1.24},
        ]

        # Call the /<pair>/mms route with query parameters
        response = client.get('/v1/BRLBTC/mms?precision=20&from=1638316800&to=1638403200')

        # Verify the response
        assert response.status_code == 200
        assert response.json == [
            {'timestamp': 1638316800, 'mms': 1.23},
            {'timestamp': 1638403200, 'mms': 1.24},
        ]

def test_search_route_missing_parameters(client):
    # Test the /<pair>/mms route with missing query parameters
    response = client.get('/v1/BRLBTC/mms?precision=20')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'missed mandatory query parameters' in response.data.decode()

def test_search_route_invalid_precision(client):
    # Test the /<pair>/mms route with an invalid precision value
    response = client.get('/v1/BRLBTC/mms?precision=invalid&from=1638316800&to=1638403200')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'missed mandatory query parameters' in response.data.decode()

def test_search_route_default_end(client):
    # Mock the MB_API class and its search_mms method
    with patch('mb_mms.services.mb_api.mb_api.MB_API') as mock_mb_api:
        mock_mb_instance = MagicMock(spec=MB_API)
        mock_mb_api.return_value = mock_mb_instance

        # Mock the search_mms method to return a list of results
        mock_mb_instance.search_mms.return_value = [
            {'timestamp': 1638316800, 'mms': 1.23},
            {'timestamp': 1638403200, 'mms': 1.24},
        ]

        # Call the /<pair>/mms route without the 'to' parameter
        response = client.get('/v1/BRLBTC/mms?precision=20&from=1638316800')

        # Verify the response
        assert response.status_code == 200
        assert response.json == [
            {'timestamp': 1638316800, 'mms': 1.23},
            {'timestamp': 1638403200, 'mms': 1.24},
        ]
