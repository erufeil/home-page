"""
Servicio para obtener datos climáticos desde OpenWeatherMap API.
"""

import requests
import logging

logger = logging.getLogger(__name__)

def get_weather_data(city, api_key):
    """
    Obtiene datos climáticos actuales para una ciudad.
    
    Args:
        city (str): Nombre de la ciudad.
        api_key (str): API Key de OpenWeatherMap.
    
    Returns:
        dict: Datos climáticos en formato:
            {
                "ciudad": str,
                "temperatura": float (en Celsius),
                "sensacion": float (en Celsius),
                "humedad": int (porcentaje),
                "descripcion": str,
                "icono": str
            }
        None: Si api_key está vacía o ocurre un error.
    """
    from backend.config import WEATHER_API_URL
    
    if not api_key or api_key.strip() == "":
        logger.warning("API Key de clima no proporcionada. Clima no disponible.")
        return None
    
    try:
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
            "lang": "es"
        }
        
        response = requests.get(WEATHER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        
        result = {
            "ciudad": city,
            "temperatura": main.get("temp", 0),
            "sensacion": main.get("feels_like", 0),
            "humedad": main.get("humidity", 0),
            "descripcion": weather.get("description", "").capitalize(),
            "icono": weather.get("icon", "")
        }
        
        logger.info(f"Datos climáticos obtenidos para {city}")
        return result
        
    except requests.exceptions.Timeout:
        logger.error("Timeout al obtener datos climáticos")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error en la solicitud de clima: {e}")
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Error procesando datos climáticos: {e}")
    
    return None