"""Tests for Watchlist API endpoints."""
import pytest

from app.models import User, Watchlist


class TestWatchlistGet:
    """Tests for GET /watchlist endpoint."""
    
    def test_get_watchlist_requires_auth(self, client):
        """Test that watchlist endpoint requires authentication."""
        response = client.get('/api/v1/watchlist')
        assert response.status_code == 401
    
    def test_get_empty_watchlist(self, client, auth_headers):
        """Test getting empty watchlist."""
        response = client.get('/api/v1/watchlist', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'items' in data
        assert 'count' in data  # L'endpoint retourne 'count', pas 'total'


class TestWatchlistAdd:
    """Tests for POST /watchlist endpoint."""
    
    def test_add_to_watchlist_requires_auth(self, client):
        """Test that adding requires authentication."""
        response = client.post('/api/v1/watchlist', json={
            'item_type': 'ticker',
            'item_id': 'AAPL',
            'item_name': 'Apple Inc.'
        })
        assert response.status_code == 401
    
    def test_add_to_watchlist_success(self, client, auth_headers):
        """Test successfully adding to watchlist."""
        response = client.post('/api/v1/watchlist', json={
            'item_type': 'ticker',
            'item_id': 'AAPL',
            'item_name': 'Apple Inc.'
        }, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'item' in data or 'message' in data
    
    def test_add_to_watchlist_missing_fields(self, client, auth_headers):
        """Test adding with missing required fields."""
        response = client.post('/api/v1/watchlist', json={
            'item_id': 'AAPL'
        }, headers=auth_headers)
        assert response.status_code == 400


class TestWatchlistUpdate:
    """Tests for PUT /watchlist/<id> endpoint."""
    
    def test_update_nonexistent_item(self, client, auth_headers):
        """Test updating non-existent item."""
        response = client.put('/api/v1/watchlist/99999', json={
            'alerts_enabled': True
        }, headers=auth_headers)
        assert response.status_code == 404


class TestWatchlistDelete:
    """Tests for DELETE /watchlist/<id> endpoint."""
    
    def test_delete_nonexistent_item(self, client, auth_headers):
        """Test deleting non-existent item."""
        response = client.delete('/api/v1/watchlist/99999', headers=auth_headers)
        assert response.status_code == 404


class TestWatchlistCheck:
    """Tests for GET /watchlist/check endpoint."""
    
    def test_check_requires_auth(self, client):
        """Test that check requires authentication."""
        response = client.get('/api/v1/watchlist/check?type=ticker&id=AAPL')
        assert response.status_code == 401
    
    def test_check_missing_parameters(self, client, auth_headers):
        """Test check with missing parameters."""
        response = client.get('/api/v1/watchlist/check', headers=auth_headers)
        assert response.status_code == 400


class TestWatchlistBulk:
    """Tests for POST /watchlist/bulk endpoint."""
    
    def test_bulk_requires_auth(self, client):
        """Test that bulk add requires authentication."""
        response = client.post('/api/v1/watchlist/bulk', json={
            'items': [{'item_type': 'ticker', 'item_id': 'AAPL', 'item_name': 'Apple'}]
        })
        assert response.status_code == 401
    
    def test_bulk_add_success(self, client, auth_headers):
        """Test bulk adding items."""
        response = client.post('/api/v1/watchlist/bulk', json={
            'items': [
                {'item_type': 'ticker', 'item_id': 'AAPL', 'item_name': 'Apple'},
                {'item_type': 'ticker', 'item_id': 'GOOGL', 'item_name': 'Google'}
            ]
        }, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'added' in data
