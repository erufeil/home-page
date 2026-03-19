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

# Database Configuration (MariaDB)
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ.get("DB_USER", "context_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "context_app")

# SQLAlchemy Configuration
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Admin Panel
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

# Session Configuration (7 days default)
SESSION_LIFETIME = int(os.environ.get("SESSION_LIFETIME", "604800"))  # 7 days in seconds
PERMANENT_SESSION_LIFETIME = SESSION_LIFETIME
SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_to_a_random_secret_key")

# Flask-Session configuration
SESSION_TYPE = os.environ.get("SESSION_TYPE", "sqlalchemy")
SESSION_SQLALCHEMY = None  # Will be set in app factory
SESSION_SQLALCHEMY_TABLE = os.environ.get("SESSION_SQLALCHEMY_TABLE", "sessions")
SESSION_PERMANENT = True
SESSION_USE_SIGNER = True
SESSION_KEY_PREFIX = "session:"

# Logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")