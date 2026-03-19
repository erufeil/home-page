"""
Servicio para obtener cotizaciones del dólar desde Bluelytics API.
"""

import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_dolar_data():
    """
    Obtiene datos de cotización del dólar y euro desde Bluelytics API.
    
    Returns:
        dict: Datos de cotización en formato:
            {
                "euro_oficial": {"compra": float, "venta": float, "promedio": float},
                "dolar_oficial": {"compra": float, "venta": float, "promedio": float},
                "dolar_blue": {"compra": float, "venta": float, "promedio": float},
                "brecha": float,
                "ultima_actualizacion": str (ISO 8601)
            }
        None: Si ocurre un error.
    """
    from backend.config import DOLAR_API_URL
    
    try:
        response = requests.get(DOLAR_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extraer valores de monedas
        euro_oficial = data.get("oficial_euro", {})
        dolar_oficial = data.get("oficial", {})
        dolar_blue = data.get("blue", {})
        
        # Calcular promedios
        euro_prom = (euro_oficial.get("value_buy", 0) + euro_oficial.get("value_sell", 0)) / 2
        oficial_prom = (dolar_oficial.get("value_buy", 0) + dolar_oficial.get("value_sell", 0)) / 2
        blue_prom = (dolar_blue.get("value_buy", 0) + dolar_blue.get("value_sell", 0)) / 2
        
        # Calcular brecha porcentual (euro oficial vs dólar oficial)
        brecha = 0
        if dolar_oficial.get("value_sell", 0) > 0:
            # Calcular cuántos dólares se necesitan para comprar 1 euro
            euros_per_dolar = euro_oficial.get("value_sell", 0) / dolar_oficial.get("value_sell", 0)
            # La brecha es la diferencia porcentual entre el valor del euro en dólares y 1
            brecha = (euros_per_dolar - 1) * 100
        
        # Formatear respuesta según contrato
        result = {
            "euro_oficial": {
                "compra": euro_oficial.get("value_buy", 0),
                "venta": euro_oficial.get("value_sell", 0),
                "promedio": euro_prom
            },
            "dolar_oficial": {
                "compra": dolar_oficial.get("value_buy", 0),
                "venta": dolar_oficial.get("value_sell", 0),
                "promedio": oficial_prom
            },
            "dolar_blue": {
                "compra": dolar_blue.get("value_buy", 0),
                "venta": dolar_blue.get("value_sell", 0),
                "promedio": blue_prom
            },
            "brecha": round(brecha, 2),
            "ultima_actualizacion": data.get("last_update", "")
        }
        
        logger.info("Datos de dólar obtenidos correctamente")
        return result
        
    except requests.exceptions.Timeout:
        logger.error("Timeout al obtener datos de dólar")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error en la solicitud de dólar: {e}")
    except (KeyError, ValueError) as e:
        logger.error(f"Error procesando datos de dólar: {e}")
    
    return None