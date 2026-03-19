"""
Aplicación Flask para landing page de dólar y clima - Multi-User Edition.
Punto de entrada principal para desarrollo y producción.
"""
import logging
from backend import create_app
from backend.config import FLASK_HOST, FLASK_PORT

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = create_app()

if __name__ == '__main__':
    logger.info(f"Iniciando servidor en {FLASK_HOST}:{FLASK_PORT}")
    logger.info(f"Modo: {'debug' if app.debug else 'production'}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)