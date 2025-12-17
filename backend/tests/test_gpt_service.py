"""
Tests unitaires pour le service GPT.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestGPTService:
    """Tests pour le service GPT."""
    
    def test_gpt_service_import(self):
        """Test import du service GPT."""
        from app.services.gpt_service import gpt_service
        assert gpt_service is not None
    
    def test_fallback_response_sports(self, app):
        """Test reponse fallback pour sports."""
        with app.app_context():
            from app.services.gpt_service import GPTService
            
            service = GPTService()
            # Forcer le mode fallback
            service.client = None
            
            result = service._get_fallback_response('sports')
            
            assert result['domain'] == 'sports'
            assert 'summary' in result
            assert 'analysis' in result
            assert 'educational_reminder' in result
            assert result['confidence'] == 0.0
    
    def test_fallback_response_finance(self, app):
        """Test reponse fallback pour finance."""
        with app.app_context():
            from app.services.gpt_service import GPTService
            
            service = GPTService()
            service.client = None
            
            result = service._get_fallback_response('finance')
            
            assert result['domain'] == 'finance'
            assert result['prediction_type'] == 'trend'
            assert result['prediction_value'] == 'NEUTRAL'
    
    def test_analyse_sport_fallback(self, app):
        """Test analyse sports en mode fallback."""
        with app.app_context():
            from app.services.gpt_service import GPTService
            
            service = GPTService()
            service.client = None
            
            match_data = {
                'match_id': '1',
                'home_team': {'name': 'Team A'},
                'away_team': {'name': 'Team B'}
            }
            
            result = service.analyse_sport(match_data, 0.65)
            
            assert result['domain'] == 'sports'
            assert result['ml_score'] == 0.65
            assert result['data_source'] == 'gpt_analysis'
    
    def test_analyse_finance_fallback(self, app):
        """Test analyse finance en mode fallback."""
        with app.app_context():
            from app.services.gpt_service import GPTService
            
            service = GPTService()
            service.client = None
            
            stock_data = {
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'current_price': 175.50,
                'indicators': {'RSI': 55}
            }
            
            result = service.analyse_finance(stock_data, 0.3)
            
            assert result['domain'] == 'finance'
            assert result['ml_score'] == 0.3
    
    @patch('app.services.gpt_service.OPENAI_AVAILABLE', False)
    def test_service_without_openai(self, app):
        """Test initialisation sans package openai."""
        with app.app_context():
            from app.services.gpt_service import GPTService
            
            service = GPTService()
            assert service.client is None
    
    def test_system_prompt_content(self, app):
        """Test contenu du prompt systeme."""
        with app.app_context():
            from app.services.gpt_service import GPTService
            
            service = GPTService()
            prompt = service._get_system_prompt()
            
            assert 'educative' in prompt.lower() or 'pedagogique' in prompt.lower()
            assert 'json' in prompt.lower()
    
    def test_create_sports_prompt(self, app):
        """Test creation du prompt sports."""
        with app.app_context():
            from app.services.gpt_service import GPTService
            
            service = GPTService()
            
            match_data = {'home_team': {'name': 'PSG'}}
            prompt = service._create_sports_prompt(match_data, 0.7)
            
            assert 'PSG' in prompt
            assert '70' in prompt  # 0.7 = 70%
            assert 'JSON' in prompt
    
    def test_create_finance_prompt(self, app):
        """Test creation du prompt finance."""
        with app.app_context():
            from app.services.gpt_service import GPTService
            
            service = GPTService()
            
            stock_data = {'symbol': 'AAPL', 'current_price': 175}
            prompt = service._create_finance_prompt(stock_data, 0.5)
            
            assert 'AAPL' in prompt
            assert 'JSON' in prompt
