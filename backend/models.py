"""
SQLAlchemy models for Context App Multi-User.
"""
import bcrypt
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend import security

Base = declarative_base()

class User(Base, UserMixin):
    """User model for authentication and user data."""
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    categories = relationship('Category', back_populates='user', cascade='all, delete-orphan')
    favorites = relationship('Favorite', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password: str) -> None:
        """Hash and set password."""
        self.password_hash = security.hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        if not self.password_hash:
            return False
        return security.check_password(password, self.password_hash)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

class Category(Base):
    """Category model for organizing favorites."""
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(50), nullable=False)
    color = Column(String(7), default='#3498db')  # hex color
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    user = relationship('User', back_populates='categories')
    favorites = relationship('Favorite', back_populates='category', cascade='all, delete-orphan')
    
    def reorder_favorites(self, new_order_ids):
        """
        Reorder favorites within this category.
        
        Args:
            new_order_ids: List of favorite IDs in desired order
        """
        # Create mapping of ID -> position
        position_map = {favorite_id: idx for idx, favorite_id in enumerate(new_order_ids)}
        
        # Update display_order for each favorite
        for favorite in self.favorites:
            if favorite.id in position_map:
                favorite.display_order = position_map[favorite.id]
    
    def __repr__(self):
        return f"<Category(id={self.id}, user_id={self.user_id}, name='{self.name}')>"

class Favorite(Base):
    """Favorite website/task model."""
    __tablename__ = 'favorite'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id', ondelete='SET NULL'), nullable=True)
    url = Column(String(500), nullable=False)
    title = Column(String(200))
    domain = Column(String(100), nullable=False)
    logo_filename = Column(String(255))
    tipo = Column(Enum('favorito', 'tarea_pendiente', name='favorite_type'), default='favorito')
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    user = relationship('User', back_populates='favorites')
    category = relationship('Category', back_populates='favorites')
    
    def move_to_category(self, new_category, new_display_order=None):
        """
        Move favorite to a different category.
        
        Args:
            new_category: Category object or None (uncategorized)
            new_display_order: Optional position in new category
        """
        old_category = self.category
        
        # Update category
        self.category = new_category
        self.category_id = new_category.id if new_category else None
        
        # Update display order if specified
        if new_display_order is not None:
            self.display_order = new_display_order
        elif new_category:
            # Place at end of new category
            max_order = max([f.display_order for f in new_category.favorites], default=-1)
            self.display_order = max_order + 1
        
        # If moving from old category, could reorder remaining favorites
        # (optional - could be handled by separate reorder method)
    
    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, url='{self.url[:30]}...')>"

class Session(Base):
    """Session model for Flask-Session SQLAlchemy backend."""
    __tablename__ = 'session'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False)
    data = Column(Text, nullable=False)
    expiry = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    def __repr__(self):
        return f"<Session(id={self.id}, session_id='{self.session_id}', expiry={self.expiry})>"