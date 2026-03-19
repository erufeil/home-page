"""
Default data seeding for new users.
Creates default categories and favorite sites.
"""
import logging
from sqlalchemy import func
from backend import db
from backend.models import Category, Favorite

logger = logging.getLogger(__name__)

# Default categories (name, color, display_order)
DEFAULT_CATEGORIES = [
    {"name": "General", "color": "#3498db", "display_order": 0},
    {"name": "Work", "color": "#2ecc71", "display_order": 1},
    {"name": "Personal", "color": "#9b59b6", "display_order": 2},
    {"name": "Social", "color": "#e74c3c", "display_order": 3},
    {"name": "Entertainment", "color": "#f39c12", "display_order": 4},
]

# Default favorite sites (all assigned to "General" category initially)
# Logo filenames correspond to files in /favorites/logos/
DEFAULT_SITES = [
    {
        "url": "https://www.google.com",
        "title": "Google",
        "domain": "google.com",
        "logo_filename": "google.com.ico",
        "tipo": "favorito",
        "category_name": "General",  # Will be mapped to category ID
    },
    {
        "url": "https://github.com",
        "title": "GitHub",
        "domain": "github.com",
        "logo_filename": "github.com.ico",
        "tipo": "favorito",
        "category_name": "General",
    },
    {
        "url": "https://www.youtube.com",
        "title": "YouTube",
        "domain": "youtube.com",
        "logo_filename": "youtube.com.ico",
        "tipo": "favorito",
        "category_name": "General",
    },
    {
        "url": "https://twitter.com",
        "title": "Twitter",
        "domain": "twitter.com",
        "logo_filename": "twitter.com.ico",
        "tipo": "favorito",
        "category_name": "General",
    },
    {
        "url": "https://www.facebook.com",
        "title": "Facebook",
        "domain": "facebook.com",
        "logo_filename": "facebook.com.png",
        "tipo": "favorito",
        "category_name": "General",
    },
    {
        "url": "https://mail.google.com",
        "title": "Gmail",
        "domain": "gmail.com",
        "logo_filename": "gmail.com.ico",
        "tipo": "favorito",
        "category_name": "General",
    },
    {
        "url": "https://outlook.live.com",
        "title": "Outlook",
        "domain": "outlook.com",
        "logo_filename": "outlook.com.ico",
        "tipo": "favorito",
        "category_name": "General",
    },
]

def seed_defaults_for_user(user_id):
    """
    Create default categories and favorite sites for a new user.
    Idempotent: will not create duplicates if they already exist.
    
    Args:
        user_id (int): ID of the user to seed defaults for.
    
    Returns:
        tuple: (categories_created_count, favorites_created_count)
    """
    categories_created = 0
    favorites_created = 0
    
    try:
        # First, ensure default categories exist
        category_map = {}  # name -> Category object
        existing_categories = db.session.query(Category).filter(
            Category.user_id == user_id
        ).all()
        
        # Map existing categories by name (case-insensitive)
        existing_by_name = {cat.name.lower(): cat for cat in existing_categories}
        
        for cat_def in DEFAULT_CATEGORIES:
            cat_name_lower = cat_def["name"].lower()
            if cat_name_lower in existing_by_name:
                # Category already exists, use it
                category = existing_by_name[cat_name_lower]
                # Optionally update color/order if different? For now, keep as is.
            else:
                # Create new category
                category = Category(
                    user_id=user_id,
                    name=cat_def["name"],
                    color=cat_def["color"],
                    display_order=cat_def["display_order"]
                )
                db.session.add(category)
                categories_created += 1
            
            category_map[cat_def["name"]] = category
        
        # Commit categories first to get IDs
        if categories_created > 0:
            db.session.commit()
            logger.info(f"Created {categories_created} default categories for user {user_id}")
        
        # Now create default favorites (only if they don't already exist)
        existing_favorites = db.session.query(Favorite).filter(
            Favorite.user_id == user_id
        ).all()
        
        # Check by domain + category to avoid duplicates
        existing_by_domain_and_category = {}
        for fav in existing_favorites:
            key = (fav.domain, fav.category_id)
            existing_by_domain_and_category[key] = fav
        
        for site_def in DEFAULT_SITES:
            category_name = site_def["category_name"]
            category = category_map.get(category_name)
            if not category:
                # Should not happen if categories seeded correctly
                logger.warning(f"Category '{category_name}' not found for user {user_id}, skipping site {site_def['title']}")
                continue
            
            key = (site_def["domain"], category.id)
            if key in existing_by_domain_and_category:
                # Favorite already exists
                continue
            
            # Determine display_order (place at end of category)
            max_order = db.session.query(
                func.max(Favorite.display_order)
            ).filter(
                Favorite.user_id == user_id,
                Favorite.category_id == category.id
            ).scalar() or -1
            
            favorite = Favorite(
                user_id=user_id,
                url=site_def["url"],
                title=site_def["title"],
                domain=site_def["domain"],
                logo_filename=site_def["logo_filename"],
                tipo=site_def["tipo"],
                category_id=category.id,
                display_order=max_order + 1
            )
            db.session.add(favorite)
            favorites_created += 1
        
        if favorites_created > 0:
            db.session.commit()
            logger.info(f"Created {favorites_created} default favorites for user {user_id}")
        
        return categories_created, favorites_created
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding defaults for user {user_id}: {e}", exc_info=True)
        raise