"""
PredictWise Backend - Application Factory
Plateforme educative d'analyse et de prediction (sports et finance).

AVERTISSEMENT: Ce projet est strictement educatif. Les predictions ne constituent
pas des conseils financiers ou de pari.
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.core.config import Config
from app.core.database import db, init_db

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_override=None):
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
            'error': 'Token expire',
            'message': 'Veuillez vous reconnecter.'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Token invalide',
            'message': str(error)
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Token manquant',
            'message': 'Authorization header requis.'
        }), 401
    
    # Initialisation de la base de donnees
    db.init_app(app)
    
    with app.app_context():
        init_db()
    
    # Enregistrement des blueprints
    from app.api.v1.auth import auth_bp
    from app.api.v1.sports import sports_bp
    from app.api.v1.finance import finance_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(sports_bp, url_prefix='/api/v1/sports')
    app.register_blueprint(finance_bp, url_prefix='/api/v1/finance')
    
    # Route de sante
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'PredictWise API'
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
                'finance': '/api/v1/finance'
            },
            'disclaimer': 'Plateforme educative - Les predictions ne constituent pas des conseils financiers ou de pari.'
        })
    
    # Gestionnaires d'erreurs globaux
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Requete invalide',
            'message': str(error)
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Ressource non trouvee',
            'message': str(error)
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Erreur interne: {error}')
        return jsonify({
            'error': 'Erreur interne du serveur',
            'message': 'Une erreur inattendue s\'est produite.'
        }), 500
    
    logger.info('Application PredictWise initialisee avec succes')
    
    return app


# Point d'entree pour le developpement
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
