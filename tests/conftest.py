import os
import sys
import pytest
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Import the app
from app import app as flask_app
from app import db

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,  # Отключаем CSRF для тестов
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'UPLOAD_FOLDER': os.path.join(project_root, 'static', 'uploads')
    })
    
    # Create the database and load test data
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner() 