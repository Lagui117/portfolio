"""
Tests pour l'endpoint dashboard live du backend.
"""

import pytest
from datetime import datetime, timedelta, timezone

from app.main import create_app
from app.core.database import db
from app.models.user import User
from app.models.prediction import Prediction
from app.core.security import create_access_token


@pytest.fixture
def app():
    """Crée une instance de l'application pour les tests."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Client de test Flask."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Crée un utilisateur de test."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            role='user'
        )
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        
        return user.id


@pytest.fixture
def auth_headers(app, test_user):
    """Headers d'authentification pour les requêtes."""
    with app.app_context():
        token = create_access_token(identity=test_user)
        return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_predictions(app, test_user):
    """Crée des prédictions de test."""
    with app.app_context():
        now = datetime.now(timezone.utc)
        predictions = []
        
        # Prédictions sports
        for i in range(3):
            pred = Prediction(
                user_id=test_user,
                prediction_type='sports',
                confidence=0.7 + (i * 0.05),
                external_match_id=f'match_{i}',
                created_at=now - timedelta(hours=i)
            )
            predictions.append(pred)
        
        # Prédictions finance
        for i in range(2):
            pred = Prediction(
                user_id=test_user,
                prediction_type='finance',
                confidence=0.65 + (i * 0.1),
                ticker=f'TICK{i}',
                created_at=now - timedelta(hours=i)
            )
            predictions.append(pred)
        
        db.session.add_all(predictions)
        db.session.commit()
        
        return [p.id for p in predictions]


class TestDashboardLiveEndpoint:
    """Tests pour l'endpoint /api/v1/dashboard/live"""
    
    def test_get_dashboard_live_unauthorized(self, client):
        """Test accès non autorisé."""
        response = client.get('/api/v1/dashboard/live')
        assert response.status_code == 401
    
    def test_get_dashboard_live_success(self, client, auth_headers, sample_predictions):
        """Test récupération des données live."""
        response = client.get('/api/v1/dashboard/live', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Vérifier la structure
        assert 'kpis' in data
        assert 'sports_summary' in data
        assert 'finance_summary' in data
        assert 'recent_activity' in data
        assert 'live_status' in data
    
    def test_dashboard_live_kpis(self, client, auth_headers, sample_predictions):
        """Test des KPIs retournés."""
        response = client.get('/api/v1/dashboard/live', headers=auth_headers)
        data = response.get_json()
        
        kpis = data['kpis']
        
        assert 'global_accuracy' in kpis
        assert 'avg_confidence' in kpis
        assert 'active_analyses' in kpis
        assert 'sports_count' in kpis
        assert 'finance_count' in kpis
        
        # Vérifier les valeurs
        assert kpis['sports_count'] == 3
        assert kpis['finance_count'] == 2
        assert kpis['active_analyses'] == 5
    
    def test_dashboard_live_sports_summary(self, client, auth_headers, sample_predictions):
        """Test du résumé sports."""
        response = client.get('/api/v1/dashboard/live', headers=auth_headers)
        data = response.get_json()
        
        sports = data['sports_summary']
        
        assert 'active_count' in sports
        assert 'avg_confidence' in sports
        assert 'recent' in sports
        
        assert sports['active_count'] == 3
        assert len(sports['recent']) <= 3
    
    def test_dashboard_live_finance_summary(self, client, auth_headers, sample_predictions):
        """Test du résumé finance."""
        response = client.get('/api/v1/dashboard/live', headers=auth_headers)
        data = response.get_json()
        
        finance = data['finance_summary']
        
        assert 'active_count' in finance
        assert 'avg_confidence' in finance
        assert 'recent' in finance
        
        assert finance['active_count'] == 2
    
    def test_dashboard_live_status(self, client, auth_headers, sample_predictions):
        """Test du statut live."""
        response = client.get('/api/v1/dashboard/live', headers=auth_headers)
        data = response.get_json()
        
        status = data['live_status']
        
        assert status['is_live'] == True
        assert 'last_updated' in status
        assert status['data_freshness'] == 'fresh'
    
    def test_dashboard_live_empty_user(self, client, app):
        """Test avec un utilisateur sans données."""
        with app.app_context():
            # Créer un nouvel utilisateur sans prédictions
            user = User(
                username='emptyuser',
                email='empty@example.com',
                role='user'
            )
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()
            
            token = create_access_token(identity=user.id)
            headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/api/v1/dashboard/live', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['kpis']['active_analyses'] == 0
        assert data['sports_summary']['active_count'] == 0
        assert data['finance_summary']['active_count'] == 0


class TestDashboardStats:
    """Tests pour l'endpoint /api/v1/dashboard/stats"""
    
    def test_get_stats_success(self, client, auth_headers, sample_predictions):
        """Test récupération des stats."""
        response = client.get('/api/v1/dashboard/stats?period=30d', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'summary' in data
        assert 'total_predictions' in data['summary']
    
    def test_get_stats_different_periods(self, client, auth_headers, sample_predictions):
        """Test différentes périodes."""
        periods = ['7d', '30d', '90d', 'all']
        
        for period in periods:
            response = client.get(f'/api/v1/dashboard/stats?period={period}', headers=auth_headers)
            assert response.status_code == 200


class TestDashboardPerformance:
    """Tests pour l'endpoint /api/v1/dashboard/performance"""
    
    def test_get_performance_success(self, client, auth_headers, sample_predictions):
        """Test récupération des performances."""
        response = client.get('/api/v1/dashboard/performance', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'period' in data
        assert 'total_predictions' in data
        assert 'confidence_distribution' in data
    
    def test_performance_by_type(self, client, auth_headers, sample_predictions):
        """Test filtre par type."""
        response = client.get('/api/v1/dashboard/performance?type=sports', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Devrait retourner uniquement les prédictions sports
        assert data['total_predictions'] == 3


class TestDashboardKPIs:
    """Tests pour l'endpoint /api/v1/dashboard/kpis"""
    
    def test_get_kpis_success(self, client, auth_headers, sample_predictions):
        """Test récupération des KPIs."""
        response = client.get('/api/v1/dashboard/kpis', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'avg_confidence' in data
        assert 'activity_score' in data
        assert 'favorite_domain' in data
        assert 'total_predictions' in data
    
    def test_kpis_favorite_domain(self, client, auth_headers, sample_predictions):
        """Test du domaine favori."""
        response = client.get('/api/v1/dashboard/kpis', headers=auth_headers)
        data = response.get_json()
        
        # 3 sports vs 2 finance = sports est favori
        assert data['favorite_domain'] == 'sports'
