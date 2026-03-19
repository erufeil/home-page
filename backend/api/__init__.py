"""
API blueprint for data endpoints: currency, weather, and favorites.
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import routes after blueprint creation to avoid circular imports
from backend.api import routes