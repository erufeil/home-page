"""
Categories blueprint for user category management.
"""
from flask import Blueprint

categories_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

# Import routes after blueprint creation to avoid circular imports
from backend.categories import routes