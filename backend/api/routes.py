"""
API routes for currency, weather, and favorites data.
"""
import logging
from datetime import datetime
from flask import jsonify, request, current_app

from backend.config import (
    DOLAR_API_URL, WEATHER_API_URL, WEATHER_CITY, 
    WEATHER_API_KEY, UPDATE_INTERVAL
)
from backend.services.dolar import get_dolar_data
from backend.services.weather import get_weather_data
from backend.services.favorites import get_favorites, add_favorite, delete_favorite  # legacy JSON functions
from flask_login import login_required, current_user
from backend import db
from backend.models import Favorite
from backend.services.favorites import (
    extract_domain, clean_domain, find_logo_url, generate_filename, download_logo, clean_domain_name
)
import requests
import re

from backend.api import api_bp

logger = logging.getLogger(__name__)

def favorite_to_legacy_dict(fav):
    """Convert Favorite SQLAlchemy object to legacy JSON format."""
    return {
        'id': str(fav.id),
        'url': fav.url,
        'title': fav.title,
        'domain': fav.domain,
        'logo': fav.logo_filename,
        'tipo': fav.tipo,
        'created_at': fav.created_at.isoformat() if fav.created_at else None
    }

def scrape_and_save_logo(url):
    """Scrape logo from URL and save to logos directory, return filename or None."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html_content = response.text
        
        logo_url = find_logo_url(html_content, url)
        if logo_url:
            logo_filename = generate_filename(url, logo_url)
            downloaded_path = download_logo(logo_url, logo_filename)
            if downloaded_path:
                return logo_filename
    except Exception as e:
        logger.error(f"Error scraping logo for {url}: {e}")
    return None

@api_bp.route('/data', methods=['GET'])
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

@api_bp.route('/favorites', methods=['GET'])
@login_required
def api_favorites():
    """Endpoint para obtener la lista de favoritos."""
    try:
        favorites = db.session.query(Favorite).filter_by(user_id=current_user.id).order_by(Favorite.display_order).all()
        return jsonify([favorite_to_legacy_dict(fav) for fav in favorites])
    except Exception as e:
        logger.error(f"Error obteniendo favoritos: {e}")
        return jsonify({"error": "No se pudieron obtener los favoritos"}), 500

@api_bp.route('/favorites', methods=['POST'])
@login_required
def api_add_favorite():
    """Endpoint para agregar un nuevo favorito."""
    try:
        data = request.get_json()
        url = data.get('url')
        title = data.get('title')
        tipo = data.get('tipo', 'favorito')  # valor por defecto
        
        if not url:
            return jsonify({"error": "URL requerida"}), 400
        
        favorite = add_favorite(url, title, tipo, use_db=True)
        return jsonify(favorite), 201
    except Exception as e:
        logger.error(f"Error agregando favorito: {e}")
        return jsonify({"error": "No se pudo agregar el favorito"}), 500

@api_bp.route('/favorites/<favorite_id>', methods=['DELETE'])
@login_required
def api_delete_favorite(favorite_id):
    """Endpoint para eliminar un favorito."""
    try:
        if delete_favorite(favorite_id, use_db=True):
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Favorito no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error eliminando favorito: {e}")
        return jsonify({"error": "No se pudo eliminar el favorito"}), 500