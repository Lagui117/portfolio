"""
Tests pour les endpoints sports.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestSportsPredict:
    """Tests pour l'endpoint /api/v1/sports/predict/<match_id>."""
    
    def test_predict_success(self, client, auth_headers):
        """Test prediction sports reussie."""
        response = client.get('/api/v1/sports/predict/1', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'match' in data
        assert 'model_score' in data
        assert 'gpt_analysis' in data
        assert 'disclaimer' in data
    
    def test_predict_match_structure(self, client, auth_headers):
        """Test structure des donnees de match."""
        response = client.get('/api/v1/sports/predict/1', headers=auth_headers)
        data = response.get_json()
        
        match = data.get('match', {})
        assert 'id' in match
        assert 'home_team' in match
        assert 'away_team' in match
        assert 'competition' in match
    
    def test_predict_gpt_analysis_structure(self, client, auth_headers):
        """Test structure de l'analyse GPT."""
        response = client.get('/api/v1/sports/predict/1', headers=auth_headers)
        data = response.get_json()
        
        gpt = data.get('gpt_analysis', {})
        assert 'domain' in gpt
        assert 'summary' in gpt
        assert 'analysis' in gpt
        assert 'confidence' in gpt
        assert 'educational_reminder' in gpt
    
    def test_predict_model_score_range(self, client, auth_headers):
        """Test que le model_score est dans une plage valide."""
        response = client.get('/api/v1/sports/predict/1', headers=auth_headers)
        data = response.get_json()
        
        model_score = data.get('model_score')
        assert model_score is not None
        assert 0 <= model_score <= 1
    
    def test_predict_without_auth(self, client):
        """Test prediction sans authentification."""
        response = client.get('/api/v1/sports/predict/1')
        
        assert response.status_code == 401
    
    def test_predict_different_match_ids(self, client, auth_headers):
        """Test prediction pour differents IDs de match."""
        for match_id in ['1', '2', '3']:
            response = client.get(f'/api/v1/sports/predict/{match_id}', headers=auth_headers)
            assert response.status_code == 200
    
    @patch('app.services.sports_api_service.sports_api_service.get_match_data')
    def test_predict_api_error(self, mock_get_match, client, auth_headers):
        """Test prediction quand l'API sports echoue."""
        mock_get_match.return_value = None
        
        response = client.get('/api/v1/sports/predict/unknown', headers=auth_headers)
        
        # Devrait retourner le mock par defaut ou 404
        assert response.status_code in [200, 404]


class TestSportsMatches:
    """Tests pour l'endpoint /api/v1/sports/matches."""
    
    def test_get_matches_success(self, client, auth_headers):
        """Test recuperation des matchs."""
        response = client.get('/api/v1/sports/matches', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'matches' in data
        assert 'count' in data
        assert isinstance(data['matches'], list)
    
    def test_get_matches_with_params(self, client, auth_headers):
        """Test recuperation des matchs avec parametres."""
        response = client.get(
            '/api/v1/sports/matches?sport=football&limit=10',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['matches']) <= 10
    
    def test_get_matches_without_auth(self, client):
        """Test recuperation des matchs sans auth."""
        response = client.get('/api/v1/sports/matches')
        
        assert response.status_code == 401


class TestSportsPredictionHistory:
    """Tests pour l'endpoint /api/v1/sports/predictions/history."""
    
    def test_get_history_empty(self, client, auth_headers):
        """Test historique vide."""
        response = client.get('/api/v1/sports/predictions/history', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'predictions' in data
        assert 'total' in data
    
    def test_get_history_after_prediction(self, client, auth_headers):
        """Test historique apres une prediction."""
        # Faire une prediction
        client.get('/api/v1/sports/predict/1', headers=auth_headers)
        
        # Verifier l'historique
        response = client.get('/api/v1/sports/predictions/history', headers=auth_headers)
        data = response.get_json()
        
        assert data['total'] >= 1
    
    def test_get_history_pagination(self, client, auth_headers):
        """Test pagination de l'historique."""
        response = client.get(
            '/api/v1/sports/predictions/history?limit=5&offset=0',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'limit' in data
        assert 'offset' in data
