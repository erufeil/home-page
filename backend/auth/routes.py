"""
Authentication routes: registration, login, logout, session management.
"""
import re
import logging
from flask import jsonify, request, make_response
from flask_login import login_user, logout_user, current_user
from sqlalchemy import func, or_
from backend import db
from backend.models import User
from backend.auth import auth_bp
from backend.security import validate_password_strength
from backend.seed import seed_defaults_for_user

logger = logging.getLogger(__name__)





@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    if not request.is_json:
        return make_response(
            jsonify({"error": "Content-Type must be application/json"}),
            400
        )
    
    data = request.get_json()
    if not data:
        return make_response(
            jsonify({"error": "Invalid or empty JSON payload"}),
            400
        )
    
    # Extract fields
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    
    # Validate required fields
    if not username:
        return make_response(
            jsonify({"error": "Username is required"}),
            400
        )
    if not email:
        return make_response(
            jsonify({"error": "Email is required"}),
            400
        )
    if not password:
        return make_response(
            jsonify({"error": "Password is required"}),
            400
        )
    
    # Validate password strength
    is_valid, message = validate_password_strength(password)
    if not is_valid:
        return make_response(
            jsonify({"error": f"Password validation failed: {message}"}),
            400
        )
    
    # Check for existing username (case-insensitive)
    existing_user = db.session.query(User).filter(
        func.lower(User.username) == func.lower(username)
    ).first()
    if existing_user:
        return make_response(
            jsonify({"error": f"Username '{username}' already exists"}),
            409
        )
    
    # Check for existing email (case-insensitive)
    existing_email = db.session.query(User).filter(
        func.lower(User.email) == func.lower(email)
    ).first()
    if existing_email:
        return make_response(
            jsonify({"error": f"Email '{email}' already registered"}),
            409
        )
    
    try:
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Automatically log in the user after registration
        login_user(user)
        
        # Seed default categories and favorites
        try:
            seed_defaults_for_user(user.id)
        except Exception as e:
            logger.error(f"Failed to seed defaults for user {user.id}: {e}", exc_info=True)
            # Continue anyway - user can create categories/favorites manually
        
        response_data = {
            "user_id": user.id,
            "username": user.username,
            "message": "User created successfully"
        }
        return make_response(jsonify(response_data), 201)
        
    except Exception as e:
        db.session.rollback()
        # Log the error in production
        logger.error(f"Registration failed: {e}", exc_info=True)
        return make_response(
            jsonify({"error": "Internal server error during registration"}),
            500
        )


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and start session."""
    if not request.is_json:
        return make_response(
            jsonify({"error": "Content-Type must be application/json"}),
            400
        )
    
    data = request.get_json()
    if not data:
        return make_response(
            jsonify({"error": "Invalid or empty JSON payload"}),
            400
        )
    
    login_field = data.get('login', '').strip()
    password = data.get('password', '').strip()
    
    if not login_field:
        return make_response(
            jsonify({"error": "Login field (username or email) is required"}),
            400
        )
    if not password:
        return make_response(
            jsonify({"error": "Password is required"}),
            400
        )
    
    # Find user by username or email (case-insensitive)
    user = db.session.query(User).filter(
        or_(
            func.lower(User.username) == func.lower(login_field),
            func.lower(User.email) == func.lower(login_field)
        )
    ).first()
    
    if not user:
        # Avoid timing attacks by still running password check on a dummy user
        # For simplicity, just return error
        return make_response(
            jsonify({"error": "Invalid username/email or password"}),
            401
        )
    
    if not user.check_password(password):
        return make_response(
            jsonify({"error": "Invalid username/email or password"}),
            401
        )
    
    if not user.is_active:
        return make_response(
            jsonify({"error": "Account is inactive"}),
            401
        )
    
    # Login successful
    print(f"AUTH LOGIN: logging in user id={user.id}, username={user.username}")
    login_user(user)
    
    response_data = {
        "user_id": user.id,
        "username": user.username,
        "message": "Login successful"
    }
    return make_response(jsonify(response_data), 200)


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """End user session."""
    if not current_user.is_authenticated:
        return make_response(
            jsonify({"error": "Not authenticated"}),
            401
        )
    
    logout_user()
    return make_response(
        jsonify({"message": "Logout successful"}),
        200
    )