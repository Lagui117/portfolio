"""
PredictWise Backend - Application Factory
Plateforme SaaS d'intelligence décisionnelle (Sports & Finance).

AVERTISSEMENT: Les analyses fournies sont à titre informatif uniquement.
Elles ne constituent pas des conseils financiers ou de paris.
"""

import os
import logging
from typing import Optional, Dict, Any
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.core.config import Config
from app.core.database import db, init_db
from app.core.errors import register_error_handlers

# Configuration du logging avancée
def configure_logging(app: Flask) -> None:
    """Configure le logging de l'application."""
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            # Optionnel: ajouter un FileHandler pour prod
        ]
    )
    
    # Configurer les loggers des bibliothèques externes
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    app.logger.setLevel(getattr(logging, log_level))

logger = logging.getLogger(__name__)


def create_app(config_override: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Factory function pour creer l'application Flask.
    
    Args:
        config_override: Dictionnaire de configuration pour override les settings par defaut.
    
    Returns:
        Application Flask configuree.
    """
    app = Flask(__name__)
    
    # Charger la configuration
    app.config.from_object(Config)
    
    # Override de configuration (pour les tests)
    if config_override:
        app.config.update(config_override)
    
    # Configurer le logging
    configure_logging(app)
    
    # Initialisation CORS
    CORS(
        app, 
        origins=app.config.get('CORS_ORIGINS', ['http://localhost:5173']),
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    )
    
    # Initialisation JWT
    jwt = JWTManager(app)
    
    # Gestionnaires d'erreurs JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': {
                'type': 'token_expired',
                'message': 'Token expire. Veuillez vous reconnecter.',
                'details': {}
            }
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': {
                'type': 'token_invalid',
                'message': 'Token invalide.',
                'details': {'reason': str(error)}
            }
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': {
                'type': 'token_missing',
                'message': 'Authorization header requis.',
                'details': {}
            }
        }), 401
    
    # Initialisation de la base de donnees
    db.init_app(app)
    
    with app.app_context():
        init_db()
    
    # Enregistrement des blueprints
    from app.api.v1.auth import auth_bp
    from app.api.v1.sports import sports_bp
    from app.api.v1.finance import finance_bp
    from app.api.v1.users import users_bp
    from app.api.v1.chat import chat_bp
    from app.api.v1.admin import admin_bp
    from app.api.v1.ai import ai_bp
    from app.api.v1.dashboard import dashboard_bp
    from app.api.v1.watchlist import watchlist_bp
    from app.api.v1.live import live_bp, start_scheduler
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(sports_bp, url_prefix='/api/v1/sports')
    app.register_blueprint(finance_bp, url_prefix='/api/v1/finance')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(chat_bp, url_prefix='/api/v1/chat')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(ai_bp, url_prefix='/api/v1/ai')
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1/dashboard')
    app.register_blueprint(watchlist_bp, url_prefix='/api/v1/watchlist')
    app.register_blueprint(live_bp, url_prefix='/api/v1/live')
    
    # Démarrer le scheduler live (en mode non-test)
    if not app.config.get('TESTING'):
        start_scheduler()
    
    # Enregistrer les gestionnaires d'erreurs centralisés
    register_error_handlers(app)
    
    # Route de sante
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'PredictWise API',
            'version': '1.0.0'
        })
    
    # Route racine
    @app.route('/')
    def root():
        return jsonify({
            'message': 'Bienvenue sur l\'API PredictWise',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/v1/auth',
                'sports': '/api/v1/sports',
                'finance': '/api/v1/finance',
                'chat': '/api/v1/chat',
                'ai': '/api/v1/ai',
                'health': '/health'
            },
            'disclaimer': 'Plateforme d\'analyse décisionnelle.'
        })
    
    logger.info('Application PredictWise initialisee avec succes')
    
    return app


# Point d'entree pour le developpement
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
