from unittest.mock import patch, MagicMock
import pytest
from requests import Session, HTTPError
from http import HTTPStatus
from mb_mms.services.mb_api.mb_api import MB_API
from mb_mms.models.pair_averages import MovingAverage
from sqlalchemy import select
from sqlalchemy.engine import Connection


@pytest.fixture
def mock_mb_api_env(monkeypatch):
    monkeypatch.setenv('MB_API', 'https://api.fake.com/{}?from{}&to{}')

@pytest.fixture
def mb_api_instance():
    # Create an instance of the MB_API class
    return MB_API()

def test_request_rate_http_error(mock_mb_api_env):
    mb_api = MB_API()

    with patch('requests.Session') as mock_session:
        mock_session_instance = MagicMock(spec=Session)
        mock_session.return_value = mock_session_instance

        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_response.raise_for_status.side_effect = HTTPError("Bad Request")
        mock_session_instance.get.return_value = mock_response

        result = mb_api.request_rate('BRLBTC', 1638316800, 1638403200)
        assert result == []

def test_request_rate_value_error(mock_mb_api_env):
    mb_api = MB_API()

    with patch('requests.Session') as mock_session:
        mock_session_instance = MagicMock(spec=Session)
        mock_session.return_value = mock_session_instance

        mock_session_instance.get.side_effect = ValueError("Invalid parameters")

        result = mb_api.request_rate('BRLBTC', 1638316800, 1638403200)
        assert result == []

def test_request_rate_unexpected_error(mock_mb_api_env):
    mb_api = MB_API()

    with patch('requests.Session') as mock_session:
        mock_session_instance = MagicMock(spec=Session)
        mock_session.return_value = mock_session_instance

        mock_session_instance.get.side_effect = Exception("Unexpected error")

        result = mb_api.request_rate('BRLBTC', 1638316800, 1638403200)
        assert result == []

def test_mms_empty_list(mb_api_instance):
    # Test the mms method with an empty list
    result = mb_api_instance.mms([])
    assert result == (0, 0)

def test_mms_single_rate(mb_api_instance):
    # Test the mms method with a single rate
    rates = [(1.23, 1638316800)]
    result = mb_api_instance.mms(rates)
    assert result == (1.23, 1638316800)

def test_mms_multiple_rates(mb_api_instance):
    # Test the mms method with multiple rates
    rates = [(1.23, 1638316800), (1.24, 1638403200), (1.25, 1638489600)]
    result = mb_api_instance.mms(rates)
    assert result == (pytest.approx(1.24), 1638489600)  # Use pytest.approx for floating-point comparison

def test_sliding_mms_empty_list(mb_api_instance):
    # Test the sliding_mms method with an empty list
    with pytest.raises(AssertionError):
        mb_api_instance.sliding_mms(delta=3, rates=None)

def test_sliding_mms_single_rate(mb_api_instance):
    # Test the sliding_mms method with a single rate
    rates = [(1.23, 1638316800)]
    result = mb_api_instance.sliding_mms(delta=3, rates=rates)
    assert result == [(None, 1638316800)]

def test_sliding_mms_multiple_rates(mb_api_instance):
    # Test the sliding_mms method with multiple rates
    rates = [(1.23, 1638316800), (1.24, 1638403200), (1.25, 1638489600)]
    result = mb_api_instance.sliding_mms(delta=3, rates=rates)
    expected_result = [
        (None, 1638316800),  # First rate, not enough data for delta=3
        (None, 1638403200),  # Second rate, not enough data for delta=3
        (pytest.approx(1.24), 1638489600),  # Third rate, average of all three
    ]
    assert result == expected_result

def test_sliding_mms_larger_delta(mb_api_instance):
    # Test the sliding_mms method with a delta larger than the number of rates
    rates = [(1.23, 1638316800), (1.24, 1638403200)]
    result = mb_api_instance.sliding_mms(delta=3, rates=rates)
    expected_result = [
        (None, 1638316800),  # First rate, not enough data for delta=3
        (None, 1638403200),  # Second rate, not enough data for delta=3
    ]
    assert result == expected_result

def test_sliding_mms_exception_handling(mb_api_instance):
    # Test the sliding_mms method with invalid input to trigger exception handling
    rates = [(1.23, 1638316800), (1.24, 1638403200)]
    result = mb_api_instance.sliding_mms(delta=0, rates=rates)  # Invalid delta
    assert result == []  # Expect an empty list due to exception handling

def test_search_mms_precision_20(mb_api_instance):
    # Mock the database connection and query execution
    with patch('mb_mms.services.mb_api.mb_api.db.get_db_engine') as mock_get_db_engine:
        # Create a mock connection
        mock_conn = MagicMock(spec=Connection)
        mock_get_db_engine.return_value.connect.return_value.__enter__.return_value = mock_conn

        # Mock the query result
        mock_result = MagicMock()
        mock_result.all.return_value = [
            MagicMock(_asdict=lambda: {'timestamp': 1638316800, 'mms': 1.23}),
            MagicMock(_asdict=lambda: {'timestamp': 1638403200, 'mms': 1.24}),
        ]
        mock_conn.execute.return_value = mock_result

        # Call the search_mms method
        result = mb_api_instance.search_mms('BTC-USD', 1638316800, 1638403200, 20)

        actual_stmt = mock_conn.execute.call_args[0][0]

        # Assert that the query was executed with the correct parameters
        expected_stmt = (
            select(MovingAverage.timestamp, MovingAverage.mms_20.label('mms'))
            .where(MovingAverage.pair == 'BTC-USD')
            .where(MovingAverage.timestamp.between(1638316800, 1638403200))
        )

        # Compare the actual and expected statements
        assert str(actual_stmt) == str(expected_stmt)

        # Assert that the result is as expected
        expected_result = [
            {'timestamp': 1638316800, 'mms': 1.23},
            {'timestamp': 1638403200, 'mms': 1.24},
        ]
        assert result == expected_result

def test_search_mms_precision_50(mb_api_instance):
    # Mock the database connection and query execution
    with patch('mb_mms.services.mb_api.mb_api.db.get_db_engine') as mock_get_db_engine:
        # Create a mock connection
        mock_conn = MagicMock(spec=Connection)
        mock_get_db_engine.return_value.connect.return_value.__enter__.return_value = mock_conn

        # Mock the query result
        mock_result = MagicMock()
        mock_result.all.return_value = [
            MagicMock(_asdict=lambda: {'timestamp': 1638316800, 'mms': 1.23}),
            MagicMock(_asdict=lambda: {'timestamp': 1638403200, 'mms': 1.24}),
        ]
        mock_conn.execute.return_value = mock_result

        # Call the search_mms method
        result = mb_api_instance.search_mms('BTC-USD', 1638316800, 1638403200, 50)

        actual_stmt = mock_conn.execute.call_args[0][0]

        # Assert that the query was executed with the correct parameters
        expected_stmt = (
            select(MovingAverage.timestamp, MovingAverage.mms_50.label('mms'))
            .where(MovingAverage.pair == 'BTC-USD')
            .where(MovingAverage.timestamp.between(1638316800, 1638403200))
        )

        # Compare the actual and expected statements
        assert str(actual_stmt) == str(expected_stmt)

        # Assert that the result is as expected
        expected_result = [
            {'timestamp': 1638316800, 'mms': 1.23},
            {'timestamp': 1638403200, 'mms': 1.24},
        ]
        assert result == expected_result

def test_search_mms_precision_200(mb_api_instance):
    # Mock the database connection and query execution
    with patch('mb_mms.services.mb_api.mb_api.db.get_db_engine') as mock_get_db_engine:
        # Create a mock connection
        mock_conn = MagicMock(spec=Connection)
        mock_get_db_engine.return_value.connect.return_value.__enter__.return_value = mock_conn

        # Mock the query result
        mock_result = MagicMock()
        mock_result.all.return_value = [
            MagicMock(_asdict=lambda: {'timestamp': 1638316800, 'mms': 1.23}),
            MagicMock(_asdict=lambda: {'timestamp': 1638403200, 'mms': 1.24}),
        ]
        mock_conn.execute.return_value = mock_result

        # Call the search_mms method
        result = mb_api_instance.search_mms('BTC-USD', 1638316800, 1638403200, 200)

        actual_stmt = mock_conn.execute.call_args[0][0]

        # Assert that the query was executed with the correct parameters
        expected_stmt = (
            select(MovingAverage.timestamp, MovingAverage.mms_200.label('mms'))
            .where(MovingAverage.pair == 'BTC-USD')
            .where(MovingAverage.timestamp.between(1638316800, 1638403200))
        )

        # Compare the actual and expected statements
        assert str(actual_stmt) == str(expected_stmt)

        # Assert that the result is as expected
        expected_result = [
            {'timestamp': 1638316800, 'mms': 1.23},
            {'timestamp': 1638403200, 'mms': 1.24},
        ]
        assert result == expected_result
