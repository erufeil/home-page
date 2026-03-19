"""
Category CRUD endpoints.
"""
import logging
from flask import jsonify, request, make_response, session
from flask_login import login_required, current_user
from sqlalchemy import or_, func
from backend.categories import categories_bp
from backend import db
from backend.models import Category, Favorite

logger = logging.getLogger(__name__)




def get_user_category(category_id):
    """
    Retrieve a category by ID if it belongs to the current user.
    Returns (category, error_response) tuple. If category not found or not owned,
    error_response is a Flask response; otherwise error_response is None.
    """
    category = db.session.get(Category, category_id)
    if not category:
        return None, make_response(
            jsonify({"error": f"Category with ID {category_id} not found"}),
            404
        )
    logger.debug(f"Checking ownership: category.user_id={category.user_id}, current_user.id={current_user.id}")
    if category.user_id != current_user.id:
        return None, make_response(
            jsonify({"error": "Access denied"}),
            403
        )
    return category, None


@categories_bp.route('', methods=['GET'])
@login_required
def list_categories():
    """
    List all categories belonging to the current user.
    
    Query parameters:
    - include_favorites: if 'true', include favorite count per category
    
    Returns:
        JSON list of categories with optional favorite counts.
    """
    include_favorites = request.args.get('include_favorites', '').lower() == 'true'
    
    categories = db.session.query(Category).filter(
        Category.user_id == current_user.id
    ).order_by(Category.display_order.asc()).all()
    
    result = []
    for cat in categories:
        cat_data = {
            'id': cat.id,
            'name': cat.name,
            'color': cat.color,
            'display_order': cat.display_order,
            'created_at': cat.created_at.isoformat() if cat.created_at else None,
            'updated_at': cat.updated_at.isoformat() if cat.updated_at else None
        }
        if include_favorites:
            cat_data['favorite_count'] = len(cat.favorites)
        result.append(cat_data)
    
    return make_response(jsonify({"categories": result}), 200)


@categories_bp.route('', methods=['POST'])
@login_required
def create_category():
    """
    Create a new category for the current user.
    
    Request body (JSON):
    - name (required): category name (max 50 chars)
    - color (optional): hex color code (default '#3498db')
    - display_order (optional): integer position (default last)
    
    Returns:
        JSON of created category.
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
    
    name = data.get('name', '').strip()
    if not name:
        return make_response(
            jsonify({"error": "Category name is required"}),
            400
        )
    if len(name) > 50:
        return make_response(
            jsonify({"error": "Category name cannot exceed 50 characters"}),
            400
        )
    
    # Check for duplicate name (case-insensitive) for this user
    existing = db.session.query(Category).filter(
        Category.user_id == current_user.id,
        func.lower(Category.name) == func.lower(name)
    ).first()
    if existing:
        return make_response(
            jsonify({"error": f"Category '{name}' already exists"}),
            409
        )
    
    color = data.get('color', '#3498db').strip()
    if not color.startswith('#') or len(color) != 7:
        color = '#3498db'  # fallback
    
    # Determine display_order (default to end)
    max_order = db.session.query(
        func.max(Category.display_order)
    ).filter(Category.user_id == current_user.id).scalar() or -1
    display_order = data.get('display_order', max_order + 1)
    
    try:
        category = Category(
            user_id=current_user.id,
            name=name,
            color=color,
            display_order=display_order
        )
        db.session.add(category)
        db.session.commit()
        
        category_data = {
            'id': category.id,
            'name': category.name,
            'color': category.color,
            'display_order': category.display_order,
            'created_at': category.created_at.isoformat() if category.created_at else None,
            'updated_at': category.updated_at.isoformat() if category.updated_at else None
        }
        return make_response(jsonify(category_data), 201)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating category: {e}", exc_info=True)
        return make_response(
            jsonify({"error": "Internal server error"}),
            500
        )


@categories_bp.route('/<int:category_id>', methods=['GET'])
@login_required
def get_category(category_id):
    """
    Retrieve a specific category.
    
    Returns:
        JSON category details with favorite count.
    """
    category, error = get_user_category(category_id)
    if error:
        return error
    
    category_data = {
        'id': category.id,
        'name': category.name,
        'color': category.color,
        'display_order': category.display_order,
        'created_at': category.created_at.isoformat() if category.created_at else None,
        'updated_at': category.updated_at.isoformat() if category.updated_at else None,
        'favorite_count': len(category.favorites)
    }
    return make_response(jsonify(category_data), 200)


@categories_bp.route('/<int:category_id>', methods=['PUT'])
@login_required
def update_category(category_id):
    """
    Update a category's properties.
    
    Request body (JSON):
    - name (optional): new name (max 50 chars)
    - color (optional): hex color
    - display_order (optional): integer position
    
    Returns:
        JSON updated category.
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
    
    category, error = get_user_category(category_id)
    if error:
        return error
    
    # Update name if provided
    if 'name' in data:
        name = data['name'].strip()
        if not name:
            return make_response(
                jsonify({"error": "Category name cannot be empty"}),
                400
            )
        if len(name) > 50:
            return make_response(
                jsonify({"error": "Category name cannot exceed 50 characters"}),
                400
            )
        # Check duplicate name (excluding current category)
        existing = db.session.query(Category).filter(
            Category.user_id == current_user.id,
            Category.id != category_id,
            func.lower(Category.name) == func.lower(name)
        ).first()
        if existing:
            return make_response(
                jsonify({"error": f"Category '{name}' already exists"}),
                409
            )
        category.name = name
    
    # Update color if provided
    if 'color' in data:
        color = data['color'].strip()
        if color.startswith('#') and len(color) == 7:
            category.color = color
        else:
            return make_response(
                jsonify({"error": "Color must be a valid hex code (e.g., #3498db)"}),
                400
            )
    
    # Update display_order if provided
    if 'display_order' in data:
        try:
            display_order = int(data['display_order'])
            category.display_order = display_order
        except (ValueError, TypeError):
            return make_response(
                jsonify({"error": "display_order must be an integer"}),
                400
            )
    
    try:
        db.session.commit()
        category_data = {
            'id': category.id,
            'name': category.name,
            'color': category.color,
            'display_order': category.display_order,
            'created_at': category.created_at.isoformat() if category.created_at else None,
            'updated_at': category.updated_at.isoformat() if category.updated_at else None,
            'favorite_count': len(category.favorites)
        }
        return make_response(jsonify(category_data), 200)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating category {category_id}: {e}", exc_info=True)
        return make_response(
            jsonify({"error": "Internal server error"}),
            500
        )


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    """
    Delete a category.
    
    If category contains favorites, their category_id will be set to NULL
    (they become uncategorized).
    
    Returns:
        Success message.
    """
    category, error = get_user_category(category_id)
    if error:
        return error
    
    try:
        # Detach favorites from this category (set category_id = NULL)
        # Use bulk update for efficiency and to avoid detached instance issues
        db.session.query(Favorite).filter_by(category_id=category.id).update({'category_id': None})
        
        db.session.delete(category)
        db.session.commit()
        
        return make_response(
            jsonify({"message": f"Category {category_id} deleted successfully"}),
            200
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting category {category_id}: {e}", exc_info=True)
        return make_response(
            jsonify({"error": "Internal server error"}),
            500
        )