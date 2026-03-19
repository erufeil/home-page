"""
Smoke tests to verify the test environment works.
"""
def test_smoke():
    """Basic smoke test."""
    assert True

def test_app_fixture(app):
    """Test that the app fixture provides a Flask app."""
    assert app is not None
    assert app.config['TESTING'] == True
    assert 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']

def test_db_fixture(db, app):
    """Test that the db fixture provides SQLAlchemy instance."""
    from sqlalchemy import text
    assert db is not None
    # Verify we can execute a simple query (need app context)
    with app.app_context():
        result = db.session.execute(text('SELECT 1')).scalar()
        assert result == 1

def test_client_fixture(client):
    """Test that client fixture works."""
    response = client.get('/')
    # Frontend routes are configured, expect successful response (200 or maybe 302)
    # But at least client returns a response
    assert response.status_code in (200, 302, 404)

def test_session_fixture(session):
    """Test that session fixture works."""
    from backend.models import User
    # Create a user
    user = User(username='smoketest', email='smoke@example.com')
    user.set_password('password')
    session.add(user)
    session.commit()
    # Retrieve
    retrieved = session.query(User).filter_by(username='smoketest').first()
    assert retrieved is not None
    assert retrieved.email == 'smoke@example.com'