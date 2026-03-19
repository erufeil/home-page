"""
Tests for SQLAlchemy models.
"""
import pytest
from backend.models import User, Category, Favorite, Session, Base

def test_user_model():
    """Test User model creation and password hashing."""
    user = User(username='testuser', email='test@example.com', is_admin=False)
    user.set_password('TestPass123')
    
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.password_hash is not None
    assert user.password_hash != 'TestPass123'  # Should be hashed
    assert user.is_admin is False
    
    # Password verification
    assert user.check_password('TestPass123') is True
    assert user.check_password('WrongPassword') is False
    
    # String representation
    repr_str = repr(user)
    assert 'User' in repr_str
    assert 'testuser' in repr_str

def test_category_model():
    """Test Category model creation."""
    category = Category(name='Test Category', color='#ff0000', display_order=1)
    
    assert category.name == 'Test Category'
    assert category.color == '#ff0000'
    assert category.display_order == 1

def test_favorite_model():
    """Test Favorite model creation."""
    favorite = Favorite(
        url='https://example.com',
        title='Example',
        domain='example.com',
        tipo='favorito',
        display_order=0
    )
    
    assert favorite.url == 'https://example.com'
    assert favorite.title == 'Example'
    assert favorite.domain == 'example.com'
    assert favorite.tipo == 'favorito'
    assert favorite.display_order == 0

def test_session_model():
    """Test Session model creation."""
    from datetime import datetime, timedelta
    expiry = datetime.utcnow() + timedelta(days=7)
    
    session = Session(
        session_id='test_session_123',
        data='{"user_id": 1}',
        expiry=expiry
    )
    
    assert session.session_id == 'test_session_123'
    assert 'user_id' in session.data
    assert session.expiry == expiry

def test_model_relationships():
    """Test relationships between models."""
    user = User(username='parent', email='parent@example.com')
    user.set_password('pass')
    
    category = Category(name='Test', user=user)
    favorite = Favorite(url='https://test.com', domain='test.com', user=user, category=category)
    
    # Test relationships
    assert category in user.categories
    assert favorite in user.favorites
    assert favorite.category == category
    assert favorite in category.favorites

def test_category_reorder_favorites():
    """Test Category.reorder_favorites() method."""
    user = User(username='test', email='test@example.com')
    category = Category(name='Test', user=user)
    
    # Create test favorites
    fav1 = Favorite(id=1, url='https://1.com', domain='1.com', user=user, category=category, display_order=0)
    fav2 = Favorite(id=2, url='https://2.com', domain='2.com', user=user, category=category, display_order=1)
    fav3 = Favorite(id=3, url='https://3.com', domain='3.com', user=user, category=category, display_order=2)
    
    category.favorites = [fav1, fav2, fav3]
    
    # Reorder: 3, 1, 2
    category.reorder_favorites([3, 1, 2])
    
    assert fav1.display_order == 1  # ID 1 at position 1
    assert fav2.display_order == 2  # ID 2 at position 2
    assert fav3.display_order == 0  # ID 3 at position 0

def test_favorite_move_to_category():
    """Test Favorite.move_to_category() method."""
    user = User(username='test', email='test@example.com')
    cat1 = Category(name='Cat1', user=user)
    cat2 = Category(name='Cat2', user=user)
    
    # Create favorites in cat1
    fav1 = Favorite(id=1, url='https://1.com', domain='1.com', user=user, category=cat1, display_order=0)
    fav2 = Favorite(id=2, url='https://2.com', domain='2.com', user=user, category=cat1, display_order=1)
    fav3 = Favorite(id=3, url='https://3.com', domain='3.com', user=user, category=cat2, display_order=0)
    
    cat1.favorites = [fav1, fav2]
    cat2.favorites = [fav3]
    
    # Move fav1 from cat1 to cat2
    fav1.move_to_category(cat2)
    
    assert fav1.category == cat2
    assert fav1.category_id == cat2.id
    assert fav1.display_order == 1  # Should be after fav3 (max_order + 1)
    assert fav1 not in cat1.favorites
    assert fav1 in cat2.favorites
    
    # Move fav2 to None (uncategorized)
    fav2.move_to_category(None)
    assert fav2.category is None
    assert fav2.category_id is None

if __name__ == '__main__':
    pytest.main([__file__, '-v'])