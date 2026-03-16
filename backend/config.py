"""
Configuración del backend para landing page de dólar y clima.
Variables pueden ser sobrescritas por variables de entorno.
"""

import os

# API URLs
DOLAR_API_URL = os.environ.get("DOLAR_API_URL", "https://api.bluelytics.com.ar/v2/latest")
WEATHER_API_URL = os.environ.get("WEATHER_API_URL", "https://api.openweathermap.org/data/2.5/weather")

# Ciudad para clima
WEATHER_CITY = os.environ.get("WEATHER_CITY", "Córdoba")

# API Key de OpenWeatherMap (requiere registro gratuito)
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

# Intervalo de actualización en segundos (para frontend)
UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", "300"))

# Configuración del servidor Flask
FLASK_HOST = os.environ.get("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.environ.get("FLASK_PORT", "5000"))

# Habilitar CORS para desarrollo (True/False)
ENABLE_CORS = os.environ.get("ENABLE_CORS", "True").lower() == "true"