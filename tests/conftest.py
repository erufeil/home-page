"""
Pytest configuration and fixtures for Context App tests.
"""
import pytest
import tempfile
import os, shutil
from backend import create_app
from backend.models import Base

# Base test configuration (URI will be overridden per test)
TEST_CONFIG = {
    'TESTING': True,
    'DEBUG': True,
    'SQLALCHEMY_DATABASE_URI': None,  # Will be set per fixture
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SECRET_KEY': 'test-secret-key',
    'ADMIN_PASSWORD': 'admin123',  # For automatic admin user creation
    'WTF_CSRF_ENABLED': False,
    'ENV': 'testing',
    # Flask-Session configuration (use filesystem for tests to avoid table conflicts)
    'SESSION_TYPE': 'filesystem',
    'SESSION_PERMANENT': True,
    'SESSION_USE_SIGNER': True,
    'SESSION_KEY_PREFIX': 'session:',
    'PERMANENT_SESSION_LIFETIME': 604800,  # 7 days
}

@pytest.fixture(scope='function')
def app():
    """
    Create a Flask application for testing using the factory.
    Uses a temporary SQLite file database for isolation.
    """
    # Create a temporary SQLite database file
    fd, db_path = tempfile.mkstemp(suffix='.sqlite')
    os.close(fd)
    
    # Create a temporary directory for session files
    session_dir = tempfile.mkdtemp(prefix='flask_session_')
    
    # Update config with the temporary database path and session directory
    config = TEST_CONFIG.copy()
    config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    config['SESSION_FILE_DIR'] = session_dir
    
    app = create_app(config)
    
    # Create tables
    with app.app_context():
        Base.metadata.create_all(bind=app.extensions['sqlalchemy'].engine)
    
    yield app
    
    # Cleanup: drop tables and delete temporary files
    with app.app_context():
        Base.metadata.drop_all(bind=app.extensions['sqlalchemy'].engine)
    try:
        os.unlink(db_path)
    except OSError:
        pass  # Ignore deletion errors
    try:
        shutil.rmtree(session_dir, ignore_errors=True)
    except OSError:
        pass

@pytest.fixture(scope='function')
def db(app):
    """
    Provide the SQLAlchemy database instance.
    """
    from backend import db as global_db
    # Ensure db is initialized with the app (already done in app fixture)
    return global_db

@pytest.fixture(scope='function')
def client(app):
    """
    Test client for making requests.
    """
    return app.test_client()

@pytest.fixture(scope='function')
def session(db, app):
    """
    Create a new database session for a test with transaction rollback.
    Uses the same connection as the app, but starts a nested transaction
    that can be rolled back at the end of each test.
    """
    with app.app_context():
        # Start a nested transaction (savepoint) that we can roll back
        connection = db.engine.connect()
        transaction = connection.begin()
        db.session.bind = connection
        
        yield db.session
        
        # Rollback the transaction and close connection
        transaction.rollback()
        connection.close()
        db.session.remove()

@pytest.fixture(scope='function')
def test_user(session):
    """
    Create a test user for authentication tests.
    """
    from backend.models import User
    user = User(username='testuser', email='test@example.com')
    user.set_password('TestPass123')
    session.add(user)
    session.commit()
    return user