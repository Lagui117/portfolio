"""
Tests pour le service API sports.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestSportsAPIService:
    """Tests pour le service API sports."""
    
    def test_service_import(self):
        """Test import du service."""
        from app.services.sports_api_service import sports_api_service
        assert sports_api_service is not None
    
    def test_get_match_data_mock(self, app):
        """Test recuperation de donnees match en mode mock."""
        with app.app_context():
            from app.services.sports_api_service import SportsAPIService
            
            service = SportsAPIService()
            service.use_mock = True
            
            result = service.get_match_data('1')
            
            assert result is not None
            assert 'match_id' in result
            assert 'home_team' in result
            assert 'away_team' in result
    
    def test_get_match_data_known_ids(self, app):
        """Test recuperation pour IDs de match connus."""
        with app.app_context():
            from app.services.sports_api_service import SportsAPIService
            
            service = SportsAPIService()
            service.use_mock = True
            
            for match_id in ['1', '2', '3']:
                result = service.get_match_data(match_id)
                assert result is not None
                assert result['match_id'] == match_id
    
    def test_get_match_data_unknown_id(self, app):
        """Test recuperation pour ID inconnu (genere donnees mock)."""
        with app.app_context():
            from app.services.sports_api_service import SportsAPIService
            
            service = SportsAPIService()
            service.use_mock = True
            
            result = service.get_match_data('999')
            
            assert result is not None
            assert result['match_id'] == '999'
    
    def test_match_data_structure(self, app):
        """Test structure des donnees de match."""
        with app.app_context():
            from app.services.sports_api_service import SportsAPIService
            
            service = SportsAPIService()
            service.use_mock = True
            
            result = service.get_match_data('1')
            
            required_fields = ['match_id', 'sport', 'league', 'home_team', 'away_team', 'odds']
            for field in required_fields:
                assert field in result
            
            # Verifier structure equipes
            assert 'name' in result['home_team']
            assert 'name' in result['away_team']
    
    def test_get_upcoming_matches(self, app):
        """Test recuperation des matchs a venir."""
        with app.app_context():
            from app.services.sports_api_service import SportsAPIService
            
            service = SportsAPIService()
            service.use_mock = True
            
            result = service.get_upcoming_matches(sport='football', limit=5)
            
            assert isinstance(result, list)
            assert len(result) <= 5
    
    @patch('app.services.sports_api_service.REQUESTS_AVAILABLE', True)
    @patch('app.services.sports_api_service.requests.get')
    def test_api_timeout(self, mock_get, app):
        """Test gestion du timeout API."""
        with app.app_context():
            from app.services.sports_api_service import SportsAPIService
            import requests
            
            mock_get.side_effect = requests.exceptions.Timeout()
            
            service = SportsAPIService()
            service.use_mock = False
            service.api_key = 'test-key'
            
            result = service.get_match_data('1')
            
            # Devrait retourner les donnees mock en fallback
            assert result is not None
    
    @patch('app.services.sports_api_service.REQUESTS_AVAILABLE', True)
    @patch('app.services.sports_api_service.requests.get')
    def test_api_http_error(self, mock_get, app):
        """Test gestion des erreurs HTTP."""
        with app.app_context():
            from app.services.sports_api_service import SportsAPIService
            import requests
            
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
            mock_get.return_value = mock_response
            
            service = SportsAPIService()
            service.use_mock = False
            service.api_key = 'test-key'
            
            result = service.get_match_data('1')
            
            # Devrait retourner les donnees mock en fallback
            assert result is not None
