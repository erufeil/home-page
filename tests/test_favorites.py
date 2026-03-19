"""
Tests for favorite CRUD endpoints with category association.
"""
import json
import pytest
from backend.models import Favorite, Category, User


@pytest.fixture
def regular_user(session):
    """Create a regular user for testing."""
    user = User(username="favoriteuser", email="favorite@example.com")
    user.set_password("FavoritePass123")
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def logged_in_client(app, regular_user):
    """Client authenticated as regular_user."""
    client = app.test_client()
    login_data = {"login": "favoriteuser", "password": "FavoritePass123"}
    response = client.post(
        "/api/auth/login",
        data=json.dumps(login_data),
        content_type="application/json"
    )
    assert response.status_code == 200
    return client


@pytest.fixture
def other_user(session):
    """Create another user to test ownership."""
    user = User(username="otherfavoriteuser", email="otherfavorite@example.com")
    user.set_password("OtherFavoritePass123")
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def other_user_client(client, other_user):
    """Client authenticated as other_user."""
    login_data = {"login": "otherfavoriteuser", "password": "OtherFavoritePass123"}
    response = client.post(
        "/api/auth/login",
        data=json.dumps(login_data),
        content_type="application/json"
    )
    assert response.status_code == 200
    return client


@pytest.fixture
def category(regular_user, session):
    """Create a category for regular_user."""
    category = Category(
        user_id=regular_user.id,
        name="Test Category",
        color="#3498db",
        display_order=0
    )
    session.add(category)
    session.commit()
    return category


@pytest.fixture
def other_category(other_user, session):
    """Create a category for other_user."""
    category = Category(
        user_id=other_user.id,
        name="Other Category",
        color="#e74c3c",
        display_order=0
    )
    session.add(category)
    session.commit()
    return category


@pytest.fixture
def favorite(regular_user, category, session):
    """Create a favorite for regular_user."""
    favorite = Favorite(
        user_id=regular_user.id,
        url="https://example.com",
        title="Example",
        domain="example.com",
        tipo="favorito",
        category_id=category.id,
        display_order=0
    )
    session.add(favorite)
    session.commit()
    return favorite


@pytest.fixture
def other_favorite(other_user, other_category, session):
    """Create a favorite for other_user."""
    favorite = Favorite(
        user_id=other_user.id,
        url="https://other.example.com",
        title="Other Example",
        domain="other.example.com",
        tipo="favorito",
        category_id=other_category.id,
        display_order=0
    )
    session.add(favorite)
    session.commit()
    return favorite


def test_list_favorites(logged_in_client, favorite):
    """GET /api/v2/favorites returns user's favorites."""
    response = logged_in_client.get("/api/v2/favorites")
    assert response.status_code == 200
    data = response.get_json()
    assert "favorites" in data
    favorites = data["favorites"]
    assert len(favorites) == 1
    assert favorites[0]["id"] == favorite.id
    assert favorites[0]["url"] == favorite.url
    assert favorites[0]["category_id"] == favorite.category_id


def test_list_favorites_filter_by_category(logged_in_client, favorite, category, session):
    """GET /api/v2/favorites?category_id=X filters correctly."""
    # Create another favorite without category
    fav2 = Favorite(
        user_id=favorite.user_id,
        url="https://example2.com",
        title="Example2",
        domain="example2.com",
        tipo="favorito",
        category_id=None,
        display_order=1
    )
    session.add(fav2)
    session.commit()
    
    # Filter by category
    response = logged_in_client.get(f"/api/v2/favorites?category_id={category.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["favorites"]) == 1
    assert data["favorites"][0]["id"] == favorite.id
    
    # Filter uncategorized
    response = logged_in_client.get("/api/v2/favorites?include_uncategorized=false")
    assert response.status_code == 200
    data = response.get_json()
    # Should only include favorite with category (fav2 excluded)
    assert len(data["favorites"]) == 1
    assert data["favorites"][0]["id"] == favorite.id


def test_create_favorite(logged_in_client, category):
    """POST /api/v2/favorites creates a new favorite."""
    fav_data = {
        "url": "https://new.example.com",
        "title": "New Site",
        "tipo": "favorito",
        "category_id": category.id
    }
    response = logged_in_client.post(
        "/api/v2/favorites",
        data=json.dumps(fav_data),
        content_type="application/json"
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["url"] == fav_data["url"]
    assert data["title"] == fav_data["title"]
    assert data["category_id"] == category.id
    assert data["domain"] == "new.example.com"
    assert data["tipo"] == "favorito"


def test_create_favorite_without_category(logged_in_client):
    """POST /api/v2/favorites works without category."""
    fav_data = {
        "url": "https://nocat.example.com",
        "title": "No Category"
    }
    response = logged_in_client.post(
        "/api/v2/favorites",
        data=json.dumps(fav_data),
        content_type="application/json"
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["category_id"] is None
    assert data["domain"] == "nocat.example.com"


def test_create_favorite_invalid_url(logged_in_client):
    """POST /api/v2/favorites rejects invalid URL."""
    fav_data = {
        "url": "not-a-url",
        "title": "Invalid"
    }
    response = logged_in_client.post(
        "/api/v2/favorites",
        data=json.dumps(fav_data),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_create_favorite_category_not_owned(logged_in_client, other_category):
    """POST /api/v2/favorites rejects category belonging to other user."""
    fav_data = {
        "url": "https://example.com",
        "title": "Test",
        "category_id": other_category.id
    }
    response = logged_in_client.post(
        "/api/v2/favorites",
        data=json.dumps(fav_data),
        content_type="application/json"
    )
    assert response.status_code == 403
    data = response.get_json()
    assert "error" in data


def test_get_favorite(logged_in_client, favorite):
    """GET /api/v2/favorites/<id> returns favorite."""
    response = logged_in_client.get(f"/api/v2/favorites/{favorite.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == favorite.id
    assert data["url"] == favorite.url


def test_get_favorite_not_found(logged_in_client):
    """GET /api/v2/favorites/<id> returns 404 for non-existent favorite."""
    response = logged_in_client.get("/api/v2/favorites/99999")
    assert response.status_code == 404


def test_get_favorite_other_user(logged_in_client, other_favorite):
    """GET /api/v2/favorites/<id> denies access to other user's favorite."""
    response = logged_in_client.get(f"/api/v2/favorites/{other_favorite.id}")
    assert response.status_code == 403


def test_update_favorite(logged_in_client, favorite, category):
    """PUT /api/v2/favorites/<id> updates favorite."""
    update_data = {
        "title": "Updated Title",
        "tipo": "tarea_pendiente",
        "display_order": 5
    }
    response = logged_in_client.put(
        f"/api/v2/favorites/{favorite.id}",
        data=json.dumps(update_data),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == update_data["title"]
    assert data["tipo"] == update_data["tipo"]
    assert data["display_order"] == update_data["display_order"]
    # Ensure other fields unchanged
    assert data["url"] == favorite.url
    assert data["category_id"] == favorite.category_id


def test_update_favorite_change_category(logged_in_client, favorite, session):
    """PUT /api/v2/favorites/<id> can change category."""
    # Create a new category for same user
    new_category = Category(
        user_id=favorite.user_id,
        name="New Category",
        color="#2ecc71",
        display_order=1
    )
    session.add(new_category)
    session.commit()
    
    update_data = {"category_id": new_category.id}
    response = logged_in_client.put(
        f"/api/v2/favorites/{favorite.id}",
        data=json.dumps(update_data),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["category_id"] == new_category.id


def test_update_favorite_remove_category(logged_in_client, favorite):
    """PUT /api/v2/favorites/<id> can remove category (set null)."""
    update_data = {"category_id": None}
    response = logged_in_client.put(
        f"/api/v2/favorites/{favorite.id}",
        data=json.dumps(update_data),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["category_id"] is None


def test_update_favorite_category_not_owned(logged_in_client, favorite, other_category):
    """PUT /api/v2/favorites/<id> rejects category belonging to other user."""
    update_data = {"category_id": other_category.id}
    response = logged_in_client.put(
        f"/api/v2/favorites/{favorite.id}",
        data=json.dumps(update_data),
        content_type="application/json"
    )
    assert response.status_code == 403


def test_update_favorite_other_user(logged_in_client, other_favorite):
    """PUT /api/v2/favorites/<id> denies access to other user's favorite."""
    update_data = {"title": "Hacked"}
    response = logged_in_client.put(
        f"/api/v2/favorites/{other_favorite.id}",
        data=json.dumps(update_data),
        content_type="application/json"
    )
    assert response.status_code == 403


def test_delete_favorite(logged_in_client, favorite, session):
    """DELETE /api/v2/favorites/<id> deletes favorite."""
    response = logged_in_client.delete(f"/api/v2/favorites/{favorite.id}")
    assert response.status_code == 200
    # Verify deleted
    fav = session.get(Favorite, favorite.id)
    assert fav is None


def test_delete_favorite_other_user(logged_in_client, other_favorite):
    """DELETE /api/v2/favorites/<id> denies access to other user's favorite."""
    response = logged_in_client.delete(f"/api/v2/favorites/{other_favorite.id}")
    assert response.status_code == 403


def test_delete_favorite_not_found(logged_in_client):
    """DELETE /api/v2/favorites/<id> returns 404 for non-existent favorite."""
    response = logged_in_client.delete("/api/v2/favorites/99999")
    assert response.status_code == 404


def test_reorder_favorites_within_category(logged_in_client, favorite, category, session):
    """PUT /api/v2/favorites/reorder reorders favorites within same category."""
    # Create additional favorites in same category
    fav2 = Favorite(
        user_id=favorite.user_id,
        url="https://example2.com",
        title="Example2",
        domain="example2.com",
        tipo="favorito",
        category_id=category.id,
        display_order=1
    )
    fav3 = Favorite(
        user_id=favorite.user_id,
        url="https://example3.com",
        title="Example3",
        domain="example3.com",
        tipo="favorito",
        category_id=category.id,
        display_order=2
    )
    session.add_all([fav2, fav3])
    session.commit()
    
    # Reorder: new order fav3, favorite, fav2
    payload = {
        "favorite_ids": [fav3.id, favorite.id, fav2.id]
    }
    response = logged_in_client.put(
        "/api/v2/favorites/reorder",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    
    # Verify new order
    session.refresh(favorite)
    session.refresh(fav2)
    session.refresh(fav3)
    assert favorite.display_order == 1
    assert fav2.display_order == 2
    assert fav3.display_order == 0
    
    # Verify category unchanged
    assert favorite.category_id == category.id
    assert fav2.category_id == category.id
    assert fav3.category_id == category.id


def test_reorder_favorites_move_to_category(logged_in_client, favorite, category, session):
    """PUT /api/v2/favorites/reorder moves favorites to different category."""
    # Create another category
    new_category = Category(
        user_id=favorite.user_id,
        name="New Category",
        color="#2ecc71",
        display_order=0
    )
    session.add(new_category)
    session.commit()
    
    # Create another favorite in same original category
    fav2 = Favorite(
        user_id=favorite.user_id,
        url="https://example2.com",
        title="Example2",
        domain="example2.com",
        tipo="favorito",
        category_id=category.id,
        display_order=1
    )
    session.add(fav2)
    session.commit()
    
    # Move both favorites to new category with new order
    payload = {
        "favorite_ids": [fav2.id, favorite.id],
        "category_id": new_category.id
    }
    response = logged_in_client.put(
        "/api/v2/favorites/reorder",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    
    # Verify new order and category
    session.refresh(favorite)
    session.refresh(fav2)
    assert favorite.display_order == 1
    assert fav2.display_order == 0
    assert favorite.category_id == new_category.id
    assert fav2.category_id == new_category.id
    
    # Original category should have no favorites
    favorites_in_original = session.query(Favorite).filter(
        Favorite.category_id == category.id
    ).all()
    assert len(favorites_in_original) == 0


def test_reorder_favorites_uncategorize(logged_in_client, favorite, category, session):
    """PUT /api/v2/favorites/reorder moves favorites to uncategorized (null)."""
    payload = {
        "favorite_ids": [favorite.id],
        "category_id": None
    }
    response = logged_in_client.put(
        "/api/v2/favorites/reorder",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    
    session.refresh(favorite)
    assert favorite.category_id is None
    assert favorite.display_order == 0


def test_reorder_favorites_missing_ids(logged_in_client, favorite):
    """PUT /api/v2/favorites/reorder returns 404 if any favorite not found/owned."""
    payload = {
        "favorite_ids": [favorite.id, 99999]
    }
    response = logged_in_client.put(
        "/api/v2/favorites/reorder",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert "99999" in data["error"]


def test_reorder_favorites_duplicate_ids(logged_in_client, favorite):
    """PUT /api/v2/favorites/reorder rejects duplicate favorite_ids."""
    payload = {
        "favorite_ids": [favorite.id, favorite.id]
    }
    response = logged_in_client.put(
        "/api/v2/favorites/reorder",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "duplicate" in data["error"].lower()


def test_reorder_favorites_category_not_owned(logged_in_client, favorite, other_category):
    """PUT /api/v2/favorites/reorder rejects category belonging to other user."""
    payload = {
        "favorite_ids": [favorite.id],
        "category_id": other_category.id
    }
    response = logged_in_client.put(
        "/api/v2/favorites/reorder",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 403


def test_reorder_favorites_other_user_favorite(logged_in_client, other_favorite):
    """PUT /api/v2/favorites/reorder rejects favorite belonging to other user."""
    payload = {
        "favorite_ids": [other_favorite.id]
    }
    response = logged_in_client.put(
        "/api/v2/favorites/reorder",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 404  # Not found because not owned


def test_reorder_favorites_empty_list(logged_in_client):
    """PUT /api/v2/favorites/reorder rejects empty favorite_ids list."""
    payload = {
        "favorite_ids": []
    }
    response = logged_in_client.put(
        "/api/v2/favorites/reorder",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_legacy_favorites_get(logged_in_client, regular_user, session):
    """GET /api/favorites returns user's favorites in legacy format."""
    # Create a favorite for the user
    favorite = Favorite(
        user_id=regular_user.id,
        url="https://example.com",
        title="Example",
        domain="example.com",
        tipo="favorito",
        category_id=None,
        display_order=0
    )
    session.add(favorite)
    session.commit()
    
    response = logged_in_client.get("/api/favorites")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    fav = data[0]
    assert fav["url"] == favorite.url
    assert fav["title"] == favorite.title
    assert fav["domain"] == favorite.domain
    assert fav["tipo"] == favorite.tipo
    assert fav["id"] == str(favorite.id)
    # logo field may be None
    assert fav["logo"] is None
    assert "created_at" in fav