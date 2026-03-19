"""
Application factory for Context App Multi-User.
"""
import logging
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
session = Session()

def create_app(config=None):
    """
    Create and configure the Flask application.
    
    Args:
        config: Optional configuration object or dictionary
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__, static_folder=None)
    
    # Load configuration
    if config is None:
        # Load from config module and environment variables
        app.config.from_object('backend.config')
    else:
        app.config.update(config)
    
    # Configure logging
    logging.basicConfig(level=app.config.get('LOG_LEVEL', 'INFO'))
    logger = logging.getLogger(__name__)
    
    # Enable CORS if configured
    if app.config.get('ENABLE_CORS', True):
        CORS(app)
        logger.info("CORS enabled for development")
    
    # Initialize extensions with app
    db.init_app(app)
    # Configure Flask-Session to use SQLAlchemy backend
    app.config['SESSION_SQLALCHEMY'] = db
    session.init_app(app)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.session_protection = 'strong'
    
    # Custom unauthorized handler for API endpoints (return JSON 401 instead of redirect)
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import jsonify, make_response
        return make_response(
            jsonify({"error": "Authentication required"}),
            401
        )
    
    # Import models and bind Base metadata to db
    from backend.models import Base, User
    from backend.security import hash_password
    with app.app_context():
        Base.metadata.bind = db.engine
        # Create tables if they don't exist (development/testing)
        env = app.config.get('ENV')
        if env in ['development', 'testing']:
            Base.metadata.create_all(bind=db.engine)
            # Flask-Session's Session model is registered with db.Model, create its table
            db.create_all()
            logger.info(f"Database tables created ({env} mode)")
        else:
            # Production: assume tables exist (created via migrations)
            logger.info(f"Running in {env} mode, assuming tables exist")
        
        # Ensure at least one admin user exists (using ADMIN_PASSWORD from config)
        admin_password = app.config.get('ADMIN_PASSWORD')
        if admin_password:
            try:
                existing_admin = db.session.query(User).filter(User.is_admin == True).first()
                if not existing_admin:
                    # Check if default admin user already exists (by username)
                    admin_user = db.session.query(User).filter(
                        User.username == 'admin'
                    ).first()
                    if not admin_user:
                        admin_user = User(
                            username='admin',
                            email='admin@example.com',
                            is_admin=True,
                            is_active=True
                        )
                        admin_user.set_password(admin_password)
                        db.session.add(admin_user)
                        db.session.commit()
                        logger.info("Default admin user created (username: admin)")
                    else:
                        # Convert existing admin user to admin
                        admin_user.is_admin = True
                        admin_user.set_password(admin_password)
                        db.session.commit()
                        logger.info("Existing admin user updated with admin privileges")
                else:
                    logger.info("Admin user already exists")
            except Exception as e:
                logger.warning(f"Cannot create admin user (tables may not exist): {e}")
        else:
            logger.warning("ADMIN_PASSWORD not set - admin user will not be created automatically")
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        import traceback, sys
        sys.stderr.write(f"\n--- LOAD_USER called with user_id={user_id} ---\n")
        traceback.print_stack(file=sys.stderr)
        user = db.session.get(User, int(user_id))
        if user:
            sys.stderr.write(f"LOAD_USER returning user id={user.id}, username={user.username}\n")
        else:
            sys.stderr.write(f"LOAD_USER user not found\n")
        return user
    

    
    # Register blueprints
    from backend.auth import auth_bp
    from backend.api import api_bp
    from backend.admin import admin_bp
    from backend.categories import categories_bp
    from backend.favorites import favorites_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(favorites_bp)
    
    # Register static file serving routes (frontend)
    from backend.frontend_routes import register_frontend_routes
    register_frontend_routes(app)
    
    # Clear Flask-Login's per-request user cache to prevent cross‑request leakage in tests
    @app.before_request
    def clear_login_user_cache():
        from flask import g
        g.pop('_login_user', None)
    
    logger.info(f"Application created with config: {app.config.get('ENV', 'production')}")
    return app