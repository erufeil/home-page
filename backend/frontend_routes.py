"""
Frontend static file serving routes.
"""
import logging
from flask import send_from_directory

logger = logging.getLogger(__name__)

def register_frontend_routes(app):
    """
    Register routes for serving frontend static files.
    
    Args:
        app: Flask application instance
    """
    @app.route('/', methods=['GET'])
    def serve_index():
        """Sirve el frontend (index.html)."""
        return send_from_directory('../frontend', 'index.html')
    
    @app.route('/<path:path>', methods=['GET'])
    def serve_static(path):
        """Sirve archivos estáticos del frontend (CSS, JS)."""
        return send_from_directory('../frontend', path)
    
    @app.route('/favorites/logos/<filename>', methods=['GET'])
    def serve_logo(filename):
        """Sirve logos de favoritos."""
        return send_from_directory('../favorites/logos', filename)
    
    logger.info("Frontend routes registered")