"""
Configuration de test et fixtures pytest.
"""

import pytest
from app.main import create_app
from app.core.database import db


@pytest.fixture
def app():
    """Cree une application Flask pour les tests."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key',
        'SECRET_KEY': 'test-secret-key',
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Cree un client de test Flask."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Cree un utilisateur et retourne les headers d'authentification."""
    # Creer un utilisateur
    response = client.post('/api/v1/auth/register', json={
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'TestPass123',
        'first_name': 'Test',
        'last_name': 'User'
    })
    
    data = response.get_json()
    token = data.get('access_token')
    
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_user_data():
    """Donnees utilisateur de test."""
    return {
        'email': 'newuser@example.com',
        'username': 'newuser',
        'password': 'SecurePass123',
        'first_name': 'New',
        'last_name': 'User'
    }
