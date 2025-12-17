"""
Configuration pytest et fixtures partagees pour tous les tests backend.
"""

import os
import sys
from datetime import datetime, timezone, timedelta

import pytest

# Ajouter le backend au path pour imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import create_app
from app.core.database import db as _db
from app.models.user import User


@pytest.fixture(scope='session')
def app():
    """
    Cree l'application Flask pour les tests avec une base de donnees en memoire.
    """
    # Configuration de test
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key-very-secure',
        'SECRET_KEY': 'test-secret-key',
        'LOG_LEVEL': 'ERROR',  # Reduire les logs pendant les tests
        'OPENAI_API_KEY': '',  # Pas d'API key reelle dans les tests
    }
    
    flask_app = create_app(config_override=test_config)
    
    # Creer le contexte
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """
    Fournit une session de base de donnees pour chaque test.
    Rollback apres chaque test pour isolation.
    """
    with app.app_context():
        # Commencer une transaction
        connection = _db.engine.connect()
        transaction = connection.begin()
        
        # Créer une scoped_session liée à la transaction
        from sqlalchemy.orm import sessionmaker, scoped_session
        session_factory = sessionmaker(bind=connection)
        Session = scoped_session(session_factory)
        
        # Sauvegarder l'ancienne session et la remplacer
        old_session = _db.session
        _db.session = Session
        
        yield _db
        
        # Rollback et cleanup
        Session.remove()
        transaction.rollback()
        connection.close()
        
        # Restaurer l'ancienne session
        _db.session = old_session


@pytest.fixture(scope='function')
def client(app, db):
    """
    Client de test Flask.
    """
    return app.test_client()


@pytest.fixture
def sample_user(db):
    """
    Cree un utilisateur de test.
    """
    user = User(
        email='test@example.com',
        username='testuser',
        first_name='Test',
        last_name='User',
        is_active=True
    )
    user.set_password('SecurePassword123!')
    
    db.session.add(user)
    db.session.commit()
    
    return user


@pytest.fixture
def sample_inactive_user(db):
    """
    Cree un utilisateur inactif pour tester les restrictions.
    """
    user = User(
        email='inactive@example.com',
        username='inactiveuser',
        is_active=False
    )
    user.set_password('Password123!')
    
    db.session.add(user)
    db.session.commit()
    
    return user


@pytest.fixture
def auth_token(app, sample_user):
    """
    Genere un token JWT valide pour l'utilisateur de test.
    """
    from app.core.security import create_access_token
    
    with app.app_context():
        token = create_access_token(sample_user.id)
        return token


@pytest.fixture
def auth_headers(auth_token):
    """
    Headers HTTP avec authentification JWT.
    """
    return {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def sample_match_data():
    """
    Donnees de match sportif pour les tests.
    """
    return {
        'id': 'match_12345',
        'home_team': {
            'name': 'Paris Saint-Germain',
            'win_rate': 0.72,
            'goals_scored_avg': 2.5,
            'goals_conceded_avg': 0.8,
            'recent_form': [1, 1, 0, 1, 1]  # W W D W W
        },
        'away_team': {
            'name': 'Olympique de Marseille',
            'win_rate': 0.58,
            'goals_scored_avg': 1.8,
            'goals_conceded_avg': 1.2,
            'recent_form': [1, 0, 1, 0, 1]  # W D W D W
        },
        'odds': {
            'home_win': 1.65,
            'draw': 3.80,
            'away_win': 5.50
        },
        'competition': 'Ligue 1',
        'date': '2025-12-20T20:00:00Z'
    }


@pytest.fixture
def sample_stock_data():
    """
    Donnees financieres pour les tests.
    """
    return {
        'symbol': 'AAPL',
        'name': 'Apple Inc.',
        'sector': 'Technology',
        'current_price': 185.50,
        'prices': [180.0, 182.5, 181.0, 183.5, 185.5],
        'volumes': [50000000, 48000000, 52000000, 49000000, 51000000],
        'indicators': {
            'rsi': 58.5,
            'macd': 2.3,
            'signal': 1.8,
            'sma_20': 182.0,
            'sma_50': 178.5,
            'volatility': 0.025
        }
    }
def sample_user_data():
    """Donnees utilisateur de test."""
    return {
        'email': 'newuser@example.com',
        'username': 'newuser',
        'password': 'SecurePass123',
        'first_name': 'New',
        'last_name': 'User'
    }
