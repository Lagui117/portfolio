"""Tests for Dashboard API endpoints."""
import pytest
from datetime import datetime, timedelta, timezone

from app.models import User, Prediction


class TestDashboardOverview:
    """Tests for /dashboard/overview endpoint."""
    
    def test_overview_requires_auth(self, client):
        """Test that overview endpoint requires authentication."""
        response = client.get('/api/v1/dashboard/overview')
        assert response.status_code == 401
    
    def test_overview_success(self, client, auth_headers):
        """Test getting overview for authenticated user."""
        response = client.get('/api/v1/dashboard/overview', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        
        # Check structure
        assert 'stats' in data
        assert 'recent_predictions' in data
    
    def test_overview_stats_structure(self, client, auth_headers):
        """Test stats structure in overview."""
        response = client.get('/api/v1/dashboard/overview', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        
        stats = data['stats']
        assert 'total_predictions' in stats


class TestDashboardHistory:
    """Tests for /dashboard/history endpoint."""
    
    def test_history_requires_auth(self, client):
        """Test that history endpoint requires authentication."""
        response = client.get('/api/v1/dashboard/history')
        assert response.status_code == 401
    
    def test_history_returns_data(self, client, auth_headers):
        """Test that history returns data."""
        response = client.get('/api/v1/dashboard/history', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'predictions' in data
        assert 'pagination' in data


class TestDashboardPerformance:
    """Tests for /dashboard/performance endpoint."""
    
    def test_performance_requires_auth(self, client):
        """Test that performance endpoint requires authentication."""
        response = client.get('/api/v1/dashboard/performance')
        assert response.status_code == 401
    
    def test_performance_returns_data(self, client, auth_headers):
        """Test performance returns expected data."""
        response = client.get('/api/v1/dashboard/performance', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        
        # Check structure exists
        assert isinstance(data, dict)


class TestDashboardKPIs:
    """Tests for /dashboard/kpis endpoint."""
    
    def test_kpis_requires_auth(self, client):
        """Test that KPIs endpoint requires authentication."""
        response = client.get('/api/v1/dashboard/kpis')
        assert response.status_code == 401
    
    def test_kpis_returns_data(self, client, auth_headers):
        """Test KPIs returns data for authenticated user."""
        response = client.get('/api/v1/dashboard/kpis', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        
        assert isinstance(data, dict)


class TestDashboardFavorites:
    """Tests for /dashboard/favorites endpoint."""
    
    def test_favorites_requires_auth(self, client):
        """Test that favorites endpoint requires authentication."""
        response = client.get('/api/v1/dashboard/favorites')
        assert response.status_code == 401
    
    def test_favorites_returns_data(self, client, auth_headers):
        """Test favorites returns data for authenticated user."""
        response = client.get('/api/v1/dashboard/favorites', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        
        # L'endpoint retourne 'finance' et 'sports', pas 'favorites'
        assert 'finance' in data
        assert 'sports' in data
