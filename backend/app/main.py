"""Main application entry point."""
import os
from flask import Flask, jsonify
from flask_restx import Api
from flask_cors import CORS

from app.core.config import config
from app.core.database import init_db

# Import API namespaces
from app.api.v1.auth import api as auth_ns
from app.api.v1.sports import api as sports_ns
from app.api.v1.finance import api as finance_ns


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
    
    # Initialize CORS
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Initialize database
    init_db(app)
    
    # Create API with Flask-RESTX
    api = Api(
        app,
        version='1.0.0',
        title='PredictWise API',
        description='API REST complète pour prédictions sportives et financières basées sur le Machine Learning',
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
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Ressource non trouvée'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Erreur interne du serveur'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {str(error)}')
        return jsonify({'error': 'Une erreur est survenue'}), 500
    
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
                'finance': '/api/v1/finance'
            }
        }, 200
    
    # Log startup
    with app.app_context():
        app.logger.info(f'🚀 PredictWise API démarré en mode {config_name}')
        app.logger.info(f'📚 Documentation disponible sur http://localhost:5000/api/docs')
    
    return app


# Create app instance
app = create_app()

if __name__ == '__main__':
    print('=' * 60)
    print('🎯 PredictWise API Server')
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
