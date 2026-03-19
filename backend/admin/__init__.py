"""
Admin blueprint for user management and administrative functions.
"""
from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Import routes after blueprint creation to avoid circular imports
from backend.admin import routes