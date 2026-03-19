"""
Default data seeding for new users.
Creates default categories and favorite sites.
Categories are loaded from preferences.json at the project root.
"""
import os
import json
import logging
from sqlalchemy import func
from backend import db
from backend.models import Category, Favorite

logger = logging.getLogger(__name__)

PREFERENCES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'preferences.json'
)

def load_default_categories():
    """Load default categories from preferences.json."""
    try:
        with open(PREFERENCES_FILE, 'r', encoding='utf-8') as f:
            prefs = json.load(f)
        return prefs.get('default_categories', [])
    except Exception as e:
        logger.warning(f"Could not load preferences.json: {e}. Using hardcoded defaults.")
        return [
            {"name": "Mensajería",       "color": "#1abc9c", "display_order": 0},
            {"name": "IA IntArtif",      "color": "#8e44ad", "display_order": 1},
            {"name": "Programación",     "color": "#2c3e50", "display_order": 2},
            {"name": "Pagos",            "color": "#27ae60", "display_order": 3},
            {"name": "Bancos",           "color": "#2980b9", "display_order": 4},
            {"name": "Tareas Pendientes","color": "#e74c3c", "display_order": 5},
        ]

def seed_defaults_for_user(user_id):
    """
    Create default categories for a new user (loaded from preferences.json).
    Idempotent: will not create duplicates if they already exist.

    Returns:
        int: number of categories created
    """
    categories_created = 0
    default_categories = load_default_categories()

    try:
        existing_categories = db.session.query(Category).filter(
            Category.user_id == user_id
        ).all()
        existing_by_name = {cat.name.lower(): cat for cat in existing_categories}

        for cat_def in default_categories:
            if cat_def["name"].lower() not in existing_by_name:
                category = Category(
                    user_id=user_id,
                    name=cat_def["name"],
                    color=cat_def["color"],
                    display_order=cat_def["display_order"]
                )
                db.session.add(category)
                categories_created += 1

        if categories_created > 0:
            db.session.commit()
            logger.info(f"Created {categories_created} default categories for user {user_id}")

        return categories_created

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding defaults for user {user_id}: {e}", exc_info=True)
        raise