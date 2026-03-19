"""
Tests for admin endpoints (user management).
"""
import json
import pytest
from backend.models import User


@pytest.fixture
def admin_user(session):
    """
    Get the admin user created automatically via ADMIN_PASSWORD.
    Assumes admin user already exists (created by app startup).
    """
    admin = session.query(User).filter(User.username == 'admin').first()
    assert admin is not None, "Admin user should have been created automatically"
    assert admin.is_admin is True
    return admin


@pytest.fixture
def admin_client(client, admin_user):
    """
    Client with admin authentication (logged in as admin).
    """
    # Login as admin
    login_data = {
        "login": "admin",
        "password": "admin123"  # matches ADMIN_PASSWORD in test config
    }
    response = client.post(
        "/api/auth/login",
        data=json.dumps(login_data),
        content_type="application/json"
    )
    assert response.status_code == 200, "Admin login should succeed"
    # client now has session cookie
    return client


@pytest.fixture
def regular_user(session):
    """Create a regular (non-admin) user for testing."""
    user = User(username="regular", email="regular@example.com")
    user.set_password("RegularPass123")
    session.add(user)
    session.commit()
    return user


def test_list_users_admin_access(admin_client, session, regular_user):
    """Admin can list users."""
    response = admin_client.get("/api/admin/users")
    assert response.status_code == 200
    data = response.get_json()
    assert "users" in data
    assert "pagination" in data
    # Should include admin and regular user
    usernames = [u["username"] for u in data["users"]]
    assert "admin" in usernames
    assert "regular" in usernames


def test_list_users_pagination(admin_client, session):
    """Pagination works correctly."""
    # Create a few more users to exceed default per_page (20)
    for i in range(5):
        user = User(username=f"user{i}", email=f"user{i}@example.com")
        user.set_password("pass")
        session.add(user)
    session.commit()
    
    response = admin_client.get("/api/admin/users?page=1&per_page=5")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["users"]) <= 5
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 5


def test_list_users_search(admin_client, session):
    """Search filters by username or email."""
    # Create a user with unique name
    user = User(username="alice", email="alice@example.com")
    user.set_password("pass")
    session.add(user)
    session.commit()
    
    response = admin_client.get("/api/admin/users?search=alice")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["users"]) == 1
    assert data["users"][0]["username"] == "alice"


def test_get_user_admin_access(admin_client, regular_user):
    """Admin can retrieve specific user details."""
    response = admin_client.get(f"/api/admin/users/{regular_user.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == regular_user.id
    assert data["username"] == regular_user.username
    assert data["email"] == regular_user.email
    assert "categories_count" in data
    assert "favorites_count" in data


def test_get_user_not_found(admin_client):
    """Admin requesting non-existent user returns 404."""
    response = admin_client.get("/api/admin/users/99999")
    assert response.status_code == 404


def test_update_user_admin_status(admin_client, regular_user):
    """Admin can promote/demote other users' admin status."""
    # Promote regular user to admin
    data = {"is_admin": True}
    response = admin_client.put(
        f"/api/admin/users/{regular_user.id}",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 200
    updated = response.get_json()
    assert updated["user"]["is_admin"] is True
    
    # Demote back
    data = {"is_admin": False}
    response = admin_client.put(
        f"/api/admin/users/{regular_user.id}",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 200
    updated = response.get_json()
    assert updated["user"]["is_admin"] is False


def test_update_user_active_status(admin_client, regular_user):
    """Admin can activate/deactivate other users."""
    data = {"is_active": False}
    response = admin_client.put(
        f"/api/admin/users/{regular_user.id}",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 200
    updated = response.get_json()
    assert updated["user"]["is_active"] is False


def test_update_user_self_admin_status_fails(admin_client, admin_user):
    """Admin cannot modify their own admin status."""
    data = {"is_admin": False}
    response = admin_client.put(
        f"/api/admin/users/{admin_user.id}",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 400
    error = response.get_json()
    assert "error" in error
    assert "Cannot modify your own admin status" in error["error"]


def test_update_user_self_deactivate_fails(admin_client, admin_user):
    """Admin cannot deactivate their own account."""
    data = {"is_active": False}
    response = admin_client.put(
        f"/api/admin/users/{admin_user.id}",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 400
    error = response.get_json()
    assert "error" in error
    assert "Cannot deactivate your own account" in error["error"]


def test_update_user_invalid_data(admin_client, regular_user):
    """Invalid data (non‑boolean) returns 400."""
    data = {"is_admin": "not-a-boolean"}
    response = admin_client.put(
        f"/api/admin/users/{regular_user.id}",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 400


def test_delete_user_admin_access(admin_client, regular_user, session):
    """Admin can delete another user."""
    user_id = regular_user.id
    response = admin_client.delete(f"/api/admin/users/{user_id}")
    assert response.status_code == 200
    
    # Verify user is gone
    deleted = session.query(User).get(user_id)
    assert deleted is None


def test_delete_user_self_fails(admin_client, admin_user):
    """Admin cannot delete their own account."""
    response = admin_client.delete(f"/api/admin/users/{admin_user.id}")
    assert response.status_code == 400
    error = response.get_json()
    assert "error" in error
    assert "Cannot delete your own account" in error["error"]


def test_delete_user_not_found(admin_client):
    """Deleting non‑existent user returns 404."""
    response = admin_client.delete("/api/admin/users/99999")
    assert response.status_code == 404


def test_admin_endpoints_require_admin_access(client, regular_user):
    """Non‑admin users cannot access admin endpoints."""
    # Login as regular user
    login_data = {"login": "regular", "password": "RegularPass123"}
    response = client.post(
        "/api/auth/login",
        data=json.dumps(login_data),
        content_type="application/json"
    )
    assert response.status_code == 200
    
    # Try admin endpoints
    response = client.get("/api/admin/users")
    assert response.status_code == 403
    
    response = client.get(f"/api/admin/users/{regular_user.id}")
    assert response.status_code == 403
    
    response = client.put(
        f"/api/admin/users/{regular_user.id}",
        data=json.dumps({"is_admin": True}),
        content_type="application/json"
    )
    assert response.status_code == 403
    
    response = client.delete(f"/api/admin/users/{regular_user.id}")
    assert response.status_code == 403


def test_admin_endpoints_require_authentication(client):
    """Unauthenticated requests are rejected with 401."""
    response = client.get("/api/admin/users")
    assert response.status_code == 401
    
    response = client.get("/api/admin/users/1")
    assert response.status_code == 401
    
    response = client.put(
        "/api/admin/users/1",
        data=json.dumps({"is_admin": True}),
        content_type="application/json"
    )
    assert response.status_code == 401
    
    response = client.delete("/api/admin/users/1")
    assert response.status_code == 401