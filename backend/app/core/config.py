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
