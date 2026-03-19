"""
Authentication blueprint for user registration, login, logout, and session management.
"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Import routes after blueprint creation to avoid circular imports
from backend.auth import routes