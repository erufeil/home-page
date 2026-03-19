"""
Tests for category CRUD endpoints.
"""
import json
import pytest
from backend.models import Category, User


@pytest.fixture
def regular_user(session):
    """Create a regular user for testing."""
    user = User(username="categoryuser", email="category@example.com")
    user.set_password("CategoryPass123")
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def logged_in_client(app, regular_user):
    """Client authenticated as regular_user."""
    client = app.test_client()
    login_data = {"login": "categoryuser", "password": "CategoryPass123"}
    response = client.post(
        "/api/auth/login",
        data=json.dumps(login_data),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    print(f"LOGGED_IN_CLIENT: logged in as user_id={data.get('user_id')}, username={data.get('username')}")
    if 'Set-Cookie' in response.headers:
        print(f"LOGGED_IN_CLIENT Set-Cookie: {response.headers.getlist('Set-Cookie')}")
    return client


@pytest.fixture
def other_user(session):
    """Create another user to test ownership."""
    user = User(username="otheruser", email="other@example.com")
    user.set_password("OtherPass123")
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def other_user_client(client, other_user):
    """Client authenticated as other_user."""
    login_data = {"login": "otheruser", "password": "OtherPass123"}
    response = client.post(
        "/api/auth/login",
        data=json.dumps(login_data),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    print(f"OTHER_USER_CLIENT: logged in as user_id={data.get('user_id')}, username={data.get('username')}")
    if 'Set-Cookie' in response.headers:
        print(f"OTHER_USER_CLIENT Set-Cookie: {response.headers.getlist('Set-Cookie')}")
    return client


def test_list_categories_empty(logged_in_client):
    """List categories when user has none."""
    response = logged_in_client.get("/api/categories")
    assert response.status_code == 200
    data = response.get_json()
    assert "categories" in data
    assert len(data["categories"]) == 0


def test_create_category_success(logged_in_client, session):
    """Create a new category."""
    data = {
        "name": "Work",
        "color": "#ff5733",
        "display_order": 0
    }
    response = logged_in_client.post(
        "/api/categories",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 201
    category_data = response.get_json()
    assert category_data["name"] == "Work"
    assert category_data["color"] == "#ff5733"
    assert category_data["display_order"] == 0
    assert "id" in category_data
    
    # Verify in database
    category = session.query(Category).get(category_data["id"])
    assert category is not None
    assert category.name == "Work"
    assert category.user.username == "categoryuser"


def test_create_category_duplicate_name(logged_in_client):
    """Cannot create two categories with same name for same user."""
    data = {"name": "Personal", "color": "#3498db"}
    response = logged_in_client.post("/api/categories", json=data)
    assert response.status_code == 201
    
    response = logged_in_client.post("/api/categories", json=data)
    assert response.status_code == 409
    error = response.get_json()
    assert "error" in error
    assert "already exists" in error["error"]


def test_create_category_missing_name(logged_in_client):
    """Missing name returns 400."""
    data = {"color": "#3498db"}
    response = logged_in_client.post("/api/categories", json=data)
    assert response.status_code == 400


def test_create_category_name_too_long(logged_in_client):
    """Name longer than 50 chars returns 400."""
    data = {"name": "A" * 51, "color": "#3498db"}
    response = logged_in_client.post("/api/categories", json=data)
    assert response.status_code == 400


def test_get_category_success(logged_in_client, session):
    """Retrieve a specific category."""
    # Create a category first
    category = Category(user_id=session.query(User).filter_by(username="categoryuser").first().id,
                        name="Study", color="#33ff57")
    session.add(category)
    session.commit()
    
    response = logged_in_client.get(f"/api/categories/{category.id}")
    assert response.status_code == 200
    category_data = response.get_json()
    assert category_data["name"] == "Study"
    assert category_data["color"] == "#33ff57"
    assert "favorite_count" in category_data


def test_get_category_not_found(logged_in_client):
    """Request non-existent category returns 404."""
    response = logged_in_client.get("/api/categories/99999")
    assert response.status_code == 404


def test_get_category_other_user(logged_in_client, other_user_client, session):
    """Cannot retrieve another user's category."""
    # Create a category belonging to other_user
    other_user = session.query(User).filter_by(username="otheruser").first()
    category = Category(user_id=other_user.id, name="Secret", color="#000000")
    session.add(category)
    session.commit()
    
    # Verify IDs are distinct
    logged_in_user = session.query(User).filter_by(username="categoryuser").first()
    other_user = session.query(User).filter_by(username="otheruser").first()
    print(f"DEBUG: logged_in_user id={logged_in_user.id}, username={logged_in_user.username}")
    print(f"DEBUG: other_user id={other_user.id}, username={other_user.username}")
    print(f"DEBUG: category user_id={category.user_id}")
    assert logged_in_user.id != other_user.id, f"Users should have different IDs: {logged_in_user.id} vs {other_user.id}"
    assert category.user_id == other_user.id, f"Category should belong to other_user but has user_id={category.user_id}"
    
    # Try to access with regular user
    print(f"DEBUG: logged_in_client object id={id(logged_in_client)}")
    print(f"DEBUG: other_user_client object id={id(other_user_client)}")
    # Print cookies (commented out due to attribute error)
    # print(f"LOGGED_IN_COOKIE_JAR: {logged_in_client.cookie_jar._cookies}")
    # print(f"OTHER_USER_COOKIE_JAR: {other_user_client.cookie_jar._cookies}")
    response = logged_in_client.get(f"/api/categories/{category.id}")
    print(f"DEBUG: logged_in_client response status={response.status_code}, data={response.get_json() if response.data else 'no data'}")
    assert response.status_code == 403
    
    # Other user can access
    response = other_user_client.get(f"/api/categories/{category.id}")
    assert response.status_code == 200


def test_update_category_success(logged_in_client, session):
    """Update category properties."""
    user = session.query(User).filter_by(username="categoryuser").first()
    category = Category(user_id=user.id, name="Old", color="#111111", display_order=5)
    session.add(category)
    session.commit()
    
    data = {
        "name": "Updated",
        "color": "#222222",
        "display_order": 10
    }
    response = logged_in_client.put(
        f"/api/categories/{category.id}",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 200
    updated = response.get_json()
    assert updated["name"] == "Updated"
    assert updated["color"] == "#222222"
    assert updated["display_order"] == 10
    
    # Verify database
    session.refresh(category)
    assert category.name == "Updated"
    assert category.color == "#222222"
    assert category.display_order == 10


def test_update_category_duplicate_name(logged_in_client, session):
    """Cannot rename to an existing category name."""
    user = session.query(User).filter_by(username="categoryuser").first()
    cat1 = Category(user_id=user.id, name="First", color="#111111")
    cat2 = Category(user_id=user.id, name="Second", color="#222222")
    session.add_all([cat1, cat2])
    session.commit()
    
    data = {"name": "Second"}
    response = logged_in_client.put(
        f"/api/categories/{cat1.id}",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 409


def test_update_category_invalid_color(logged_in_client, session):
    """Invalid hex color returns 400."""
    user = session.query(User).filter_by(username="categoryuser").first()
    category = Category(user_id=user.id, name="Test", color="#111111")
    session.add(category)
    session.commit()
    
    data = {"color": "nothex"}
    response = logged_in_client.put(
        f"/api/categories/{category.id}",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 400


def test_update_category_other_user(logged_in_client, other_user_client, session):
    """Cannot update another user's category."""
    other_user = session.query(User).filter_by(username="otheruser").first()
    category = Category(user_id=other_user.id, name="Other", color="#333333")
    session.add(category)
    session.commit()
    
    data = {"name": "Hacked"}
    response = logged_in_client.put(
        f"/api/categories/{category.id}",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 403
    
    # Other user can update
    response = other_user_client.put(
        f"/api/categories/{category.id}",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 200


def test_delete_category_success(logged_in_client, session):
    """Delete a category."""
    user = session.query(User).filter_by(username="categoryuser").first()
    category = Category(user_id=user.id, name="ToDelete", color="#444444")
    session.add(category)
    session.commit()
    
    response = logged_in_client.delete(f"/api/categories/{category.id}")
    assert response.status_code == 200
    
    # Verify category removed
    deleted = session.query(Category).get(category.id)
    assert deleted is None


def test_delete_category_with_favorites(logged_in_client, session):
    """Delete category, favorites become uncategorized."""
    from backend.models import Favorite
    user = session.query(User).filter_by(username="categoryuser").first()
    category = Category(user_id=user.id, name="WithFavs", color="#555555")
    session.add(category)
    session.commit()
    
    # Create a favorite in this category
    favorite = Favorite(
        user_id=user.id,
        category_id=category.id,
        url="https://example.com",
        domain="example.com",
        title="Example"
    )
    session.add(favorite)
    session.commit()
    
    response = logged_in_client.delete(f"/api/categories/{category.id}")
    assert response.status_code == 200
    
    # Favorite should have category_id = None
    session.refresh(favorite)
    assert favorite.category_id is None
    assert favorite.category is None


def test_delete_category_other_user(logged_in_client, other_user_client, session):
    """Cannot delete another user's category."""
    other_user = session.query(User).filter_by(username="otheruser").first()
    category = Category(user_id=other_user.id, name="Other", color="#666666")
    session.add(category)
    session.commit()
    
    response = logged_in_client.delete(f"/api/categories/{category.id}")
    assert response.status_code == 403
    
    # Other user can delete
    response = other_user_client.delete(f"/api/categories/{category.id}")
    assert response.status_code == 200


def test_list_categories_with_favorite_count(logged_in_client, session):
    """Include favorite count when requested."""
    from backend.models import Favorite
    user = session.query(User).filter_by(username="categoryuser").first()
    category = Category(user_id=user.id, name="WithFavs", color="#777777")
    session.add(category)
    session.commit()
    
    # Add two favorites
    fav1 = Favorite(user_id=user.id, category_id=category.id,
                    url="https://1.com", domain="1.com")
    fav2 = Favorite(user_id=user.id, category_id=category.id,
                    url="https://2.com", domain="2.com")
    session.add_all([fav1, fav2])
    session.commit()
    
    response = logged_in_client.get("/api/categories?include_favorites=true")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["categories"]) == 1
    assert data["categories"][0]["name"] == "WithFavs"
    assert data["categories"][0].get("favorite_count") == 2


def test_authentication_required(client):
    """Endpoints require authentication."""
    # GET list
    response = client.get("/api/categories")
    assert response.status_code == 401
    
    # POST create
    response = client.post("/api/categories", json={"name": "Test"})
    assert response.status_code == 401
    
    # GET single
    response = client.get("/api/categories/1")
    assert response.status_code == 401
    
    # PUT update
    response = client.put("/api/categories/1", json={"name": "Test"})
    assert response.status_code == 401
    
    # DELETE
    response = client.delete("/api/categories/1")
    assert response.status_code == 401