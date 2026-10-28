import os
import sys

import pytest

# Use an in-memory database and make the server/ modules importable.
os.environ['DATABASE_URL'] = 'sqlite://'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from app import app as flask_app  # noqa: E402
from models import db  # noqa: E402


@pytest.fixture
def app():
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
