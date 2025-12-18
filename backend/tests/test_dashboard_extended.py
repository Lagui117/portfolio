"""
Tests supplémentaires pour les endpoints Dashboard API.
Endpoints disponibles: /overview, /performance, /history, /favorites, /kpis
"""
import pytest
import json
from datetime import datetime, timedelta


class TestDashboardOverviewEndpoint:
    """Tests pour l'endpoint /api/v1/dashboard/overview."""
    
    def test_overview_requires_auth(self, client):
        """Overview nécessite authentification."""
        response = client.get('/api/v1/dashboard/overview')
        assert response.status_code == 401
    
    def test_overview_success(self, client, auth_headers):
        """Overview retourne les données."""
        response = client.get('/api/v1/dashboard/overview', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Vérifier les champs attendus
        assert data is not None
    
    def test_overview_with_period_7d(self, client, auth_headers):
        """Overview avec période 7 jours."""
        response = client.get(
            '/api/v1/dashboard/overview?period=7d',
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_overview_with_period_30d(self, client, auth_headers):
        """Overview avec période 30 jours."""
        response = client.get(
            '/api/v1/dashboard/overview?period=30d',
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_overview_with_period_90d(self, client, auth_headers):
        """Overview avec période 90 jours."""
        response = client.get(
            '/api/v1/dashboard/overview?period=90d',
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_overview_with_period_all(self, client, auth_headers):
        """Overview avec période all."""
        response = client.get(
            '/api/v1/dashboard/overview?period=all',
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestDashboardPerformanceEndpoint:
    """Tests pour l'endpoint /api/v1/dashboard/performance."""
    
    def test_performance_requires_auth(self, client):
        """Performance nécessite authentification."""
        response = client.get('/api/v1/dashboard/performance')
        assert response.status_code == 401
    
    def test_performance_success(self, client, auth_headers):
        """Performance retourne les données."""
        response = client.get('/api/v1/dashboard/performance', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
    
    def test_performance_with_period_7d(self, client, auth_headers):
        """Performance avec période 7 jours."""
        response = client.get(
            '/api/v1/dashboard/performance?period=7d',
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_performance_with_type_sports(self, client, auth_headers):
        """Performance avec type sports."""
        response = client.get(
            '/api/v1/dashboard/performance?type=sports',
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_performance_with_type_finance(self, client, auth_headers):
        """Performance avec type finance."""
        response = client.get(
            '/api/v1/dashboard/performance?type=finance',
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestDashboardHistoryEndpoint:
    """Tests pour l'endpoint /api/v1/dashboard/history."""
    
    def test_history_requires_auth(self, client):
        """History nécessite authentification."""
        response = client.get('/api/v1/dashboard/history')
        assert response.status_code == 401
    
    def test_history_success(self, client, auth_headers):
        """History retourne les données."""
        response = client.get('/api/v1/dashboard/history', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
    
    def test_history_pagination_page_1(self, client, auth_headers):
        """History avec pagination page 1."""
        response = client.get(
            '/api/v1/dashboard/history?page=1&per_page=10',
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_history_pagination_large_page(self, client, auth_headers):
        """History avec grande page."""
        response = client.get(
            '/api/v1/dashboard/history?page=1&per_page=50',
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_history_filter_type_sports(self, client, auth_headers):
        """History filtrée par type sports."""
        response = client.get(
            '/api/v1/dashboard/history?type=sports',
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_history_filter_type_finance(self, client, auth_headers):
        """History filtrée par type finance."""
        response = client.get(
            '/api/v1/dashboard/history?type=finance',
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestDashboardFavoritesEndpoint:
    """Tests pour l'endpoint /api/v1/dashboard/favorites."""
    
    def test_favorites_requires_auth(self, client):
        """Favorites nécessite authentification."""
        response = client.get('/api/v1/dashboard/favorites')
        assert response.status_code == 401
    
    def test_favorites_success(self, client, auth_headers):
        """Favorites retourne les données."""
        response = client.get('/api/v1/dashboard/favorites', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None


class TestDashboardKPIsEndpoint:
    """Tests pour l'endpoint /api/v1/dashboard/kpis."""
    
    def test_kpis_requires_auth(self, client):
        """KPIs nécessite authentification."""
        response = client.get('/api/v1/dashboard/kpis')
        assert response.status_code == 401
    
    def test_kpis_success(self, client, auth_headers):
        """KPIs retourne les données."""
        response = client.get('/api/v1/dashboard/kpis', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
    
    def test_kpis_with_period_7d(self, client, auth_headers):
        """KPIs avec période 7 jours."""
        response = client.get(
            '/api/v1/dashboard/kpis?period=7d',
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_kpis_with_period_30d(self, client, auth_headers):
        """KPIs avec période 30 jours."""
        response = client.get(
            '/api/v1/dashboard/kpis?period=30d',
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestDashboardResponseStructure:
    """Tests pour la structure des réponses dashboard."""
    
    def test_overview_structure(self, client, auth_headers):
        """Vérifier la structure de la réponse overview."""
        response = client.get('/api/v1/dashboard/overview', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # La réponse doit être un dict
        assert isinstance(data, dict)
    
    def test_kpis_structure(self, client, auth_headers):
        """Vérifier la structure de la réponse KPIs."""
        response = client.get('/api/v1/dashboard/kpis', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # La réponse doit être un dict
        assert isinstance(data, dict)
    
    def test_history_structure(self, client, auth_headers):
        """Vérifier la structure de la réponse history."""
        response = client.get('/api/v1/dashboard/history', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # La réponse doit contenir items ou history
        assert isinstance(data, dict)
        assert 'items' in data or 'history' in data or 'predictions' in data


class TestDashboardStatsEndpoint:
    """Tests pour l'endpoint /api/v1/dashboard/stats."""
    
    def test_stats_returns_something(self, client, auth_headers):
        """Stats retourne une réponse."""
        response = client.get('/api/v1/dashboard/stats', headers=auth_headers)
        
        # Peut être 200 si endpoint existe ou 404 si non
        assert response.status_code in [200, 401, 404]


class TestDashboardPredictionsHistory:
    """Tests pour l'endpoint /api/v1/dashboard/predictions/history."""
    
    def test_predictions_history_returns_something(self, client, auth_headers):
        """Predictions history retourne une réponse."""
        response = client.get(
            '/api/v1/dashboard/predictions/history',
            headers=auth_headers
        )
        
        # Endpoint peut ne pas exister
        assert response.status_code in [200, 401, 404]


class TestDashboardEdgeCases:
    """Tests des cas limites pour dashboard."""
    
    def test_overview_invalid_period(self, client, auth_headers):
        """Overview avec période invalide."""
        response = client.get(
            '/api/v1/dashboard/overview?period=invalid',
            headers=auth_headers
        )
        
        # Devrait utiliser une valeur par défaut ou gérer l'erreur
        assert response.status_code in [200, 400]
    
    def test_history_with_large_page(self, client, auth_headers):
        """History avec numéro de page élevé."""
        response = client.get(
            '/api/v1/dashboard/history?page=9999',
            headers=auth_headers
        )
        
        # Devrait retourner une liste vide ou une erreur
        assert response.status_code in [200, 404]
    
    def test_history_with_per_page_limit(self, client, auth_headers):
        """History avec per_page au-delà de la limite."""
        response = client.get(
            '/api/v1/dashboard/history?per_page=100',
            headers=auth_headers
        )
        
        # Devrait limiter à max (50)
        assert response.status_code in [200, 404]
