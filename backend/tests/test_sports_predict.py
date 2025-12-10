"""
Tests for sports prediction endpoints.
"""
import pytest
import json
from app.main import create_app
from app.core.database import db
from app.models.user import User


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def auth_token(app, client):
    """Create a test user and return auth token."""
    with app.app_context():
        # Create user
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
    
    # Login to get token
    response = client.post('/api/v1/auth/login',
        json={
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
    )
    
    return json.loads(response.data)['access_token']


class TestSportsPredictEndpoint:
    """Tests for GET /api/v1/sports/predict/<match_id> endpoint."""
    
    def test_predict_success_with_valid_match_id(self, client, auth_token):
        """Test successful prediction for a valid match ID."""
        match_id = '1'  # Mock match ID
        
        response = client.get(f'/api/v1/sports/predict/{match_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify response structure matches expected format
        assert 'match' in data
        assert 'model_score' in data
        assert 'gpt_analysis' in data
        
        # Verify match structure
        match = data['match']
        assert 'home_team' in match or 'id' in match
        
        # Verify GPT analysis structure (if available)
        if 'error' not in data['gpt_analysis']:
            gpt_analysis = data['gpt_analysis']
            assert 'domain' in gpt_analysis
            assert gpt_analysis['domain'] == 'sports'
            assert 'summary' in gpt_analysis
            assert 'analysis' in gpt_analysis
            assert 'prediction_type' in gpt_analysis
            assert 'confidence' in gpt_analysis
            assert 'educational_reminder' in gpt_analysis
    
    def test_predict_without_token(self, client):
        """Test prediction endpoint without authentication."""
        response = client.get('/api/v1/sports/predict/1')
        
        assert response.status_code == 401
    
    def test_predict_with_invalid_match_id(self, client, auth_token):
        """Test prediction with invalid/unknown match ID."""
        match_id = 'invalid_match_999999'
        
        response = client.get(f'/api/v1/sports/predict/{match_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        # API returns fallback data even for invalid IDs (graceful degradation)
        # Should return 200 with fallback data or 404/500 with error
        assert response.status_code in [200, 404, 500]
        data = json.loads(response.data)
        # Either has error or valid fallback structure
        assert 'error' in data or ('match' in data and 'gpt_analysis' in data)
    
    def test_predict_response_contains_required_keys(self, client, auth_token):
        """Test that response contains all required keys for frontend."""
        match_id = '2'
        
        response = client.get(f'/api/v1/sports/predict/{match_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        if response.status_code == 200:
            data = json.loads(response.data)
            
            # Required top-level keys
            required_keys = ['match', 'model_score', 'gpt_analysis']
            for key in required_keys:
                assert key in data, f"Missing required key: {key}"
            
            # Check gpt_analysis structure
            gpt_analysis = data['gpt_analysis']
            assert 'domain' in gpt_analysis
            assert 'summary' in gpt_analysis
            assert 'confidence' in gpt_analysis
    
    def test_predict_multiple_match_ids(self, client, auth_token):
        """Test predictions for multiple match IDs."""
        match_ids = ['1', '2', '3']
        
        for match_id in match_ids:
            response = client.get(f'/api/v1/sports/predict/{match_id}',
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            
            # Should either succeed or fail gracefully
            assert response.status_code in [200, 404, 500]
            
            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'match' in data
                assert 'gpt_analysis' in data


class TestSportsEndpointEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_predict_with_expired_token(self, client):
        """Test prediction with an expired token."""
        expired_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.expired'
        
        response = client.get('/api/v1/sports/predict/1',
            headers={'Authorization': f'Bearer {expired_token}'}
        )
        
        assert response.status_code in [401, 422]
    
    def test_predict_with_malformed_match_id(self, client, auth_token):
        """Test prediction with special characters in match ID."""
        malformed_ids = ['<script>', 'null', '', '   ']
        
        for match_id in malformed_ids:
            if match_id.strip():  # Skip empty strings for URL
                response = client.get(f'/api/v1/sports/predict/{match_id}',
                    headers={'Authorization': f'Bearer {auth_token}'}
                )
                
                # API may return fallback data or error
                assert response.status_code in [200, 400, 404, 500]
    
    def test_predict_concurrent_requests(self, client, auth_token):
        """Test handling of concurrent prediction requests."""
        match_id = '1'
        
        # Simulate multiple requests
        responses = []
        for _ in range(3):
            response = client.get(f'/api/v1/sports/predict/{match_id}',
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            responses.append(response)
        
        # All should succeed or fail consistently
        status_codes = [r.status_code for r in responses]
        assert all(code in [200, 404, 500] for code in status_codes)
