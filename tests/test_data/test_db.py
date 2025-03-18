from unittest.mock import MagicMock
import pytest
from sqlalchemy.orm import Session
from src.mb_mms.services.data.db import get_db_engine, get_db_session
from flask import Flask, g

@pytest.fixture
def mock_db_env(monkeypatch):
    monkeypatch.setenv('DB_URL', 'mysql+pymysql://foo:bar@localhost:3306/mb')

@pytest.fixture
def mock_flask_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def mock_db_session():
    session = MagicMock(spec=Session)
    return session

def test_get_db_engine(mock_db_env, mock_flask_app):
    with mock_flask_app.test_request_context():
        g.pop('db', None)
        engine = get_db_engine()

        assert engine is not None
        assert g.db is not None
        assert g.db == engine


def test_get_db_session(mock_db_env):
    session = get_db_session()
    assert session is not None
    assert isinstance(session, Session)
