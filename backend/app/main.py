"""Main application entry point."""
import os
import logging
from flask import Flask, jsonify
from flask_restx import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import HTTPException

from app.core.config import config
from app.core.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import API namespaces
from app.api.v1.auth import api as auth_ns
from app.api.v1.sports import api as sports_ns
from app.api.v1.finance import api as finance_ns
from app.api.v1.users import api as users_ns
from app.api.v1.ai import api as ai_ns


def create_app(config_name: str = None) -> Flask:
    """Create and configure Flask application.
    
    Args:
        config_name: Configuration environment name (development, production, testing)
        
    Returns:
        Configured Flask application instance
    """
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize CORS with specific configuration
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         supports_credentials=True)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token expiré', 'message': 'Veuillez vous reconnecter'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Token invalide', 'message': str(error)}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Token manquant', 'message': 'Authorization header requis'}), 401
    
    # Initialize database
    init_db(app)
    
    # Create API with Flask-RESTX
    api = Api(
        app,
        version='1.0.0',
        title='PredictWise API',
        description='API REST pour prédictions sportives et financières éducatives',
        doc='/api/docs',
        prefix='/api/v1',
        authorizations={
            'Bearer': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'JWT Authorization header. Format: "Bearer {token}"'
            }
        },
        security='Bearer'
    )
    
    # Register namespaces
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(sports_ns, path='/sports')
    api.add_namespace(finance_ns, path='/finance')
    api.add_namespace(users_ns, path='/users')
    api.add_namespace(ai_ns, path='/ai')
    
    # Global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Requête invalide', 'message': str(error)}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Ressource non trouvée'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal server error: {str(error)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        response = {
            'error': error.name,
            'message': error.description
        }
        return jsonify(response), error.code
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f'Unhandled exception: {str(error)}', exc_info=True)
        return jsonify({'error': 'Une erreur est survenue', 'message': str(error)}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f'Unhandled exception: {str(error)}', exc_info=True)
        return jsonify({'error': 'Une erreur est survenue', 'message': str(error)}), 500
    
    # Health check endpoint
    @app.route('/health')
    def health():
        """Health check endpoint for monitoring."""
        return {
            'status': 'healthy',
            'version': '1.0.0',
            'environment': config_name
        }, 200
    
    @app.route('/')
    def index():
        """Root endpoint with API information."""
        return {
            'message': 'Bienvenue sur l\'API PredictWise',
            'version': '1.0.0',
            'documentation': '/api/docs',
            'endpoints': {
                'auth': '/api/v1/auth',
                'sports': '/api/v1/sports',
                'finance': '/api/v1/finance',
                'users': '/api/v1/users',
                'ai': '/api/v1/ai'
            }
        }, 200
    
    # Log startup
    with app.app_context():
        logger.info(f'PredictWise API démarré en mode {config_name}')
        logger.info(f'Documentation disponible sur /api/docs')
    
    return app


# Create app instance
app = create_app()

if __name__ == '__main__':
    print('=' * 60)
    print('PredictWise API Server')
    print('=' * 60)
    print(f'Environment: {os.getenv("FLASK_ENV", "development")}')
    print(f'Server: http://localhost:5000')
    print(f'Docs: http://localhost:5000/api/docs')
    print('=' * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
