"""
Aplicación Flask para landing page de dólar y clima.
"""

import logging
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

from config import (
    DOLAR_API_URL, WEATHER_API_URL, WEATHER_CITY, 
    WEATHER_API_KEY, UPDATE_INTERVAL, FLASK_HOST, FLASK_PORT, ENABLE_CORS
)
from services.dolar import get_dolar_data
from services.weather import get_weather_data
from services.favorites import get_favorites, add_favorite, delete_favorite

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=None)

# Habilitar CORS si está configurado
if ENABLE_CORS:
    CORS(app)
    logger.info("CORS habilitado para desarrollo")

@app.route('/api/data', methods=['GET'])
def api_data():
    """Endpoint que retorna datos combinados de dólar y clima."""
    timestamp = datetime.now().isoformat()
    
    # Obtener datos de monedas
    dolar_data = get_dolar_data()
    if dolar_data is None:
        logger.warning("No se pudieron obtener datos de monedas")
        dolar_data = {
            "euro_oficial": {"compra": 0, "venta": 0, "promedio": 0},
            "dolar_oficial": {"compra": 0, "venta": 0, "promedio": 0},
            "dolar_blue": {"compra": 0, "venta": 0, "promedio": 0},
            "brecha": 0,
            "ultima_actualizacion": ""
        }
    
    # Obtener datos de clima
    weather_data = get_weather_data(WEATHER_CITY, WEATHER_API_KEY)
    if weather_data is None:
        logger.info("Clima no disponible (API key no configurada o error)")
        weather_data = {
            "ciudad": WEATHER_CITY,
            "temperatura": 0,
            "sensacion": 0,
            "humedad": 0,
            "descripcion": "No disponible",
            "icono": ""
        }
    
    response = {
        "timestamp": timestamp,
        "dolar": dolar_data,
        "clima": weather_data,
        "update_interval": UPDATE_INTERVAL
    }
    
    logger.info("Datos enviados via API")
    return jsonify(response)

@app.route('/', methods=['GET'])
def serve_index():
    """Sirve el frontend (index.html)."""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    """Sirve archivos estáticos del frontend (CSS, JS)."""
    return send_from_directory('../frontend', path)

@app.route('/api/favorites', methods=['GET'])
def api_favorites():
    """Endpoint para obtener la lista de favoritos."""
    try:
        favorites = get_favorites()
        return jsonify(favorites)
    except Exception as e:
        logger.error(f"Error obteniendo favoritos: {e}")
        return jsonify({"error": "No se pudieron obtener los favoritos"}), 500

@app.route('/api/favorites', methods=['POST'])
def api_add_favorite():
    """Endpoint para agregar un nuevo favorito."""
    try:
        data = request.get_json()
        url = data.get('url')
        title = data.get('title')
        tipo = data.get('tipo', 'favorito')  # valor por defecto
        
        if not url:
            return jsonify({"error": "URL requerida"}), 400
        
        favorite = add_favorite(url, title, tipo)
        return jsonify(favorite), 201
    except Exception as e:
        logger.error(f"Error agregando favorito: {e}")
        return jsonify({"error": "No se pudo agregar el favorito"}), 500

@app.route('/api/favorites/<favorite_id>', methods=['DELETE'])
def api_delete_favorite(favorite_id):
    """Endpoint para eliminar un favorito."""
    try:
        if delete_favorite(favorite_id):
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Favorito no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error eliminando favorito: {e}")
        return jsonify({"error": "No se pudo eliminar el favorito"}), 500

@app.route('/favorites/logos/<filename>', methods=['GET'])
def serve_logo(filename):
    """Sirve logos de favoritos."""
    return send_from_directory('../favorites/logos', filename)

if __name__ == '__main__':
    logger.info(f"Iniciando servidor en {FLASK_HOST}:{FLASK_PORT}")
    logger.info(f"API Dólar: {DOLAR_API_URL}")
    logger.info(f"API Clima: {WEATHER_API_URL}")
    logger.info(f"Ciudad clima: {WEATHER_CITY}")
    logger.info(f"Intervalo actualización: {UPDATE_INTERVAL}s")
    
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)