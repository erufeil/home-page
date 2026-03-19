"""
Favorites blueprint for user favorites with category association.
"""
from flask import Blueprint

favorites_bp = Blueprint('favorites', __name__, url_prefix='/api/v2/favorites')

# Import routes after blueprint creation to avoid circular imports
from backend.favorites import routes