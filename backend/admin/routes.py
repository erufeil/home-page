"""
Admin routes for user management and administrative functions.
"""
import logging
from flask import jsonify, request, make_response, current_app
from flask_login import current_user
from sqlalchemy import or_, func
from backend.admin import admin_bp
from backend.admin.decorators import admin_required
from backend import db
from backend.models import User

logger = logging.getLogger(__name__)


@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """
    List all users (paginated).
    
    Query parameters:
    - page: page number (default 1)
    - per_page: items per page (default 20, max 100)
    - search: optional search term (username or email)
    
    Returns:
        JSON list of users (excluding password_hash)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        
        # Limit per_page to prevent abuse
        if per_page > 100:
            per_page = 100
        if per_page < 1:
            per_page = 20
        
        # Build query
        query = db.session.query(User)
        
        if search:
            search_filter = or_(
                func.lower(User.username).like(f'%{search.lower()}%'),
                func.lower(User.email).like(f'%{search.lower()}%')
            )
            query = query.filter(search_filter)
        
        # Order by creation date descending
        query = query.order_by(User.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = []
        for user in pagination.items:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            })
        
        response = {
            'users': users_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total_pages': pagination.pages,
                'total_items': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
        
        return make_response(jsonify(response), 200)
        
    except Exception as e:
        logger.error(f"Error listing users: {e}", exc_info=True)
        return make_response(
            jsonify({"error": "Internal server error"}),
            500
        )


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """
    Get detailed information about a specific user.
    """
    try:
        user = db.session.get(User, user_id)
        if not user:
            return make_response(
                jsonify({"error": f"User with ID {user_id} not found"}),
                404
            )
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'categories_count': len(user.categories),
            'favorites_count': len(user.favorites)
        }
        
        return make_response(jsonify(user_data), 200)
        
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}", exc_info=True)
        return make_response(
            jsonify({"error": "Internal server error"}),
            500
        )


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """
    Update user properties (is_admin, is_active).
    
    Request body (JSON):
    - is_admin (optional): boolean
    - is_active (optional): boolean
    
    Note: Cannot modify own admin status (to prevent self‑lockout).
    """
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
    
    try:
        user = db.session.get(User, user_id)
        if not user:
            return make_response(
                jsonify({"error": f"User with ID {user_id} not found"}),
                404
            )
        
        # Prevent self‑modification of admin status
        if user.id == current_user.id and 'is_admin' in data:
            return make_response(
                jsonify({"error": "Cannot modify your own admin status"}),
                400
            )
        
        # Update fields if provided
        if 'is_admin' in data:
            if not isinstance(data['is_admin'], bool):
                return make_response(
                    jsonify({"error": "is_admin must be boolean"}),
                    400
                )
            user.is_admin = data['is_admin']
        
        if 'is_active' in data:
            if not isinstance(data['is_active'], bool):
                return make_response(
                    jsonify({"error": "is_active must be boolean"}),
                    400
                )
            # Prevent self‑deactivation
            if user.id == current_user.id and data['is_active'] is False:
                return make_response(
                    jsonify({"error": "Cannot deactivate your own account"}),
                    400
                )
            user.is_active = data['is_active']
        
        db.session.commit()
        
        return make_response(
            jsonify({
                "message": "User updated successfully",
                "user": {
                    'id': user.id,
                    'username': user.username,
                    'is_admin': user.is_admin,
                    'is_active': user.is_active
                }
            }),
            200
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user {user_id}: {e}", exc_info=True)
        return make_response(
            jsonify({"error": "Internal server error"}),
            500
        )


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    Delete a user account (hard delete).
    
    Note: Cannot delete your own account.
    """
    try:
        user = db.session.get(User, user_id)
        if not user:
            return make_response(
                jsonify({"error": f"User with ID {user_id} not found"}),
                404
            )
        
        # Prevent self‑deletion
        if user.id == current_user.id:
            return make_response(
                jsonify({"error": "Cannot delete your own account"}),
                400
            )
        
        db.session.delete(user)
        db.session.commit()
        
        return make_response(
            jsonify({"message": f"User {user_id} deleted successfully"}),
            200
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user {user_id}: {e}", exc_info=True)
        return make_response(
            jsonify({"error": "Internal server error"}),
            500
        )