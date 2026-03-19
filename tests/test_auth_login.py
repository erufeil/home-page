"""
Tests for user login and logout endpoints.
"""
import json
import pytest
from backend.models import User


def test_login_success_username(client, session):
    """Test successful login with username."""
    # Create a user
    user = User(username="testuser", email="test@example.com")
    user.set_password("SecurePass123")
    session.add(user)
    session.flush()
    
    # Attempt login with username
    data = {
        "login": "testuser",
        "password": "SecurePass123"
    }
    response = client.post(
        "/api/auth/login",
        data=json.dumps(data),
        content_type="application/json"
    )
    
    assert response.status_code == 200
    response_data = response.get_json()
    assert "user_id" in response_data
    assert response_data["username"] == "testuser"
    assert "message" in response_data


def test_login_success_email(client, session):
    """Test successful login with email."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("SecurePass123")
    session.add(user)
    session.flush()
    
    data = {
        "login": "test@example.com",
        "password": "SecurePass123"
    }
    response = client.post("/api/auth/login", json=data)
    
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data["username"] == "testuser"


def test_login_invalid_username(client, session):
    """Test login with non-existent username."""
    data = {
        "login": "nonexistent",
        "password": "whatever"
    }
    response = client.post("/api/auth/login", json=data)
    
    assert response.status_code == 401
    assert "invalid" in response.get_json().get("error", "").lower()


def test_login_invalid_password(client, session):
    """Test login with wrong password."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("SecurePass123")
    session.add(user)
    session.flush()
    
    data = {
        "login": "testuser",
        "password": "WrongPassword"
    }
    response = client.post("/api/auth/login", json=data)
    
    assert response.status_code == 401
    assert "invalid" in response.get_json().get("error", "").lower()


def test_login_missing_fields(client):
    """Test login with missing required fields."""
    # Missing login
    data = {"password": "SecurePass123"}
    response = client.post("/api/auth/login", json=data)
    assert response.status_code == 400
    
    # Missing password
    data = {"login": "testuser"}
    response = client.post("/api/auth/login", json=data)
    assert response.status_code == 400
    
    # Empty JSON
    response = client.post("/api/auth/login", json={})
    assert response.status_code == 400


def test_login_inactive_user(client, session):
    """Test login for inactive user (if is_active=False)."""
    user = User(username="inactive", email="inactive@example.com")
    user.set_password("SecurePass123")
    user.is_active = False
    session.add(user)
    session.flush()
    
    data = {
        "login": "inactive",
        "password": "SecurePass123"
    }
    response = client.post("/api/auth/login", json=data)
    
    # Should reject inactive user
    assert response.status_code == 401
    assert "inactive" in response.get_json().get("error", "").lower()


def test_logout_success(client, session):
    """Test successful logout after login."""
    # Create and login user
    user = User(username="testuser", email="test@example.com")
    user.set_password("SecurePass123")
    session.add(user)
    session.flush()
    
    # Login first
    login_data = {"login": "testuser", "password": "SecurePass123"}
    client.post("/api/auth/login", json=login_data)
    
    # Now logout
    response = client.post("/api/auth/logout")
    
    assert response.status_code == 200
    assert "success" in response.get_json().get("message", "").lower()


def test_logout_without_login(client):
    """Test logout when not logged in."""
    response = client.post("/api/auth/logout")
    # Should still succeed (no-op) or return error? We'll assume 401.
    # For now, expect 401 unauthorized.
    assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])