"""
Configuration de l'application PredictWise.
Charge les variables d'environnement depuis .env
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()


class Config:
    """Configuration de l'application."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    ENV = os.getenv('FLASK_ENV', 'development')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///predictwise.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG and ENV == 'development'
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES_DAYS', 30))
    )
    JWT_ALGORITHM = 'HS256'
    
    # CORS - En production, spécifier uniquement les origines nécessaires
    cors_origins_str = os.getenv('CORS_ORIGINS', 'http://localhost:5173')
    CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(',')]
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_TIMEOUT = int(os.getenv('OPENAI_TIMEOUT', 30))
    
    # APIs externes
    SPORTS_API_KEY = os.getenv('SPORTS_API_KEY', '')
    SPORTS_API_HOST = os.getenv('SPORTS_API_HOST', 'api-football-v1.p.rapidapi.com')
    USE_MOCK_SPORTS_API = os.getenv('USE_MOCK_SPORTS_API', 'true').lower() == 'true'
    
    FINANCE_API_KEY = os.getenv('FINANCE_API_KEY', '')
    USE_MOCK_FINANCE_API = os.getenv('USE_MOCK_FINANCE_API', 'true').lower() == 'true'
    
    # Cache
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_DEFAULT_TTL = int(os.getenv('CACHE_DEFAULT_TTL', 60))
    
    # Live Mode Configuration
    LIVE_MODE_ENABLED = os.getenv('LIVE_MODE_ENABLED', 'true').lower() == 'true'
    
    # TTL par type de ressource (secondes)
    LIVE_TTL_FINANCE_TICKER = int(os.getenv('LIVE_TTL_FINANCE_TICKER', 15))
    LIVE_TTL_FINANCE_LIST = int(os.getenv('LIVE_TTL_FINANCE_LIST', 60))
    LIVE_TTL_SPORTS_MATCH = int(os.getenv('LIVE_TTL_SPORTS_MATCH', 30))
    LIVE_TTL_SPORTS_LIST = int(os.getenv('LIVE_TTL_SPORTS_LIST', 120))
    LIVE_TTL_AI_ANALYSIS = int(os.getenv('LIVE_TTL_AI_ANALYSIS', 300))
    LIVE_TTL_DASHBOARD = int(os.getenv('LIVE_TTL_DASHBOARD', 60))
    
    # Polling intervals recommandés (secondes)
    LIVE_POLL_FINANCE_FAST = int(os.getenv('LIVE_POLL_FINANCE_FAST', 10))
    LIVE_POLL_FINANCE_NORMAL = int(os.getenv('LIVE_POLL_FINANCE_NORMAL', 30))
    LIVE_POLL_SPORTS_FAST = int(os.getenv('LIVE_POLL_SPORTS_FAST', 30))
    LIVE_POLL_SPORTS_NORMAL = int(os.getenv('LIVE_POLL_SPORTS_NORMAL', 60))
    
    # Background scheduler intervals (secondes)
    SCHEDULER_FINANCE_WATCHLIST = int(os.getenv('SCHEDULER_FINANCE_WATCHLIST', 30))
    SCHEDULER_SPORTS_MATCHES = int(os.getenv('SCHEDULER_SPORTS_MATCHES', 60))
    
    # Seuils pour recalcul IA
    AI_RECALC_PRICE_THRESHOLD = float(os.getenv('AI_RECALC_PRICE_THRESHOLD', 0.3))  # 0.3%
    AI_RECALC_ODDS_THRESHOLD = float(os.getenv('AI_RECALC_ODDS_THRESHOLD', 0.05))   # 5%
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Chemins ML
    ML_MODELS_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        '..', 'ml', 'models'
    )


class TestingConfig(Config):
    """Configuration pour les tests."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=300)
    USE_MOCK_SPORTS_API = True
    USE_MOCK_FINANCE_API = True


# Dictionnaire de configurations
config = {
    'default': Config,
    'testing': TestingConfig,
}


# Instance globale pour acces facile
settings = Config()
