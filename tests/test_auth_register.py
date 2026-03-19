"""
Tests for user registration endpoint.
"""
import json
import pytest
from backend.models import User


def test_register_success(client, session):
    """Test successful user registration."""
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123"
    }
    
    response = client.post(
        "/api/auth/register",
        data=json.dumps(data),
        content_type="application/json"
    )
    
    assert response.status_code == 201
    response_data = response.get_json()
    assert "user_id" in response_data
    assert response_data["username"] == "testuser"
    assert "message" in response_data
    
    # Verify user in database
    user = session.query(User).filter_by(username="testuser").first()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.check_password("SecurePass123")
    assert not user.is_admin


def test_register_missing_fields(client):
    """Test registration with missing required fields."""
    # Missing username
    data = {"email": "test@example.com", "password": "SecurePass123"}
    response = client.post("/api/auth/register", json=data)
    assert response.status_code == 400
    
    # Missing email
    data = {"username": "testuser", "password": "SecurePass123"}
    response = client.post("/api/auth/register", json=data)
    assert response.status_code == 400
    
    # Missing password
    data = {"username": "testuser", "email": "test@example.com"}
    response = client.post("/api/auth/register", json=data)
    assert response.status_code == 400
    
    # Empty JSON
    response = client.post("/api/auth/register", json={})
    assert response.status_code == 400


def test_register_duplicate_username(client, session):
    """Test registration with duplicate username."""
    # Create existing user
    user = User(username="existing", email="existing@example.com")
    user.set_password("password")
    session.add(user)
    session.flush()
    
    # Attempt to register with same username
    data = {
        "username": "existing",
        "email": "new@example.com",
        "password": "SecurePass123"
    }
    response = client.post("/api/auth/register", json=data)
    assert response.status_code == 409
    assert "username" in response.get_json().get("error", "").lower()


def test_register_duplicate_email(client, session):
    """Test registration with duplicate email."""
    # Create existing user
    user = User(username="existing", email="existing@example.com")
    user.set_password("password")
    session.add(user)
    session.flush()
    
    # Attempt to register with same email (different username)
    data = {
        "username": "newuser",
        "email": "existing@example.com",
        "password": "SecurePass123"
    }
    response = client.post("/api/auth/register", json=data)
    assert response.status_code == 409
    assert "email" in response.get_json().get("error", "").lower()


def test_register_weak_password(client):
    """Test registration with weak password."""
    # Too short
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "short"
    }
    response = client.post("/api/auth/register", json=data)
    assert response.status_code == 400
    assert "password" in response.get_json().get("error", "").lower()
    
    # No numbers
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "NoNumbersHere"
    }
    response = client.post("/api/auth/register", json=data)
    assert response.status_code == 400
    
    # No letters
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456789"
    }
    response = client.post("/api/auth/register", json=data)
    assert response.status_code == 400


def test_register_case_insensitive_duplicate(client, session):
    """Test duplicate detection is case-insensitive for username and email."""
    user = User(username="TestUser", email="Test@Example.com")
    user.set_password("password")
    session.add(user)
    session.flush()
    
    # Same username different case
    data = {
        "username": "testuser",  # lowercase
        "email": "different@example.com",
        "password": "SecurePass123"
    }
    response = client.post("/api/auth/register", json=data)
    assert response.status_code == 409
    
    # Same email different case
    data = {
        "username": "different",
        "email": "test@example.com",  # lowercase
        "password": "SecurePass123"
    }
    response = client.post("/api/auth/register", json=data)
    assert response.status_code == 409


if __name__ == "__main__":
    pytest.main([__file__, "-v"])