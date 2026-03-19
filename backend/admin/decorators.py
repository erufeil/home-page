"""
Admin decorators for protecting admin-only routes.
"""
from functools import wraps
from flask import jsonify, current_app
from flask_login import current_user


def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    
    Checks:
    1. User is authenticated (logged in)
    2. User has is_admin = True
    
    Returns 403 if not admin, 401 if not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        if not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function