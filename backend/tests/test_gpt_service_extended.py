"""
Tests supplémentaires pour GPTService.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock


class TestGPTServiceInit:
    """Tests pour l'initialisation de GPTService."""
    
    def test_import_gpt_service(self):
        """Tester l'import du service."""
        from app.services.gpt_service import GPTService
        assert GPTService is not None
    
    def test_init_creates_instance(self):
        """Initialisation crée une instance."""
        from app.services.gpt_service import GPTService
        service = GPTService()
        assert service is not None
        assert hasattr(service, 'model')
    
    def test_init_has_api_key_attribute(self):
        """L'instance a un attribut api_key."""
        from app.services.gpt_service import GPTService
        service = GPTService()
        assert hasattr(service, 'api_key')


class TestGPTServiceAnalyseSport:
    """Tests pour la méthode analyse_sport."""
    
    def test_analyse_sport_returns_dict(self):
        """Analyse sport retourne un dictionnaire."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        
        match_data = {
            'match_id': 'test_123',
            'home_team': {'name': 'PSG'},
            'away_team': {'name': 'OM'},
            'competition': 'Ligue 1'
        }
        
        result = service.analyse_sport(match_data)
        
        assert isinstance(result, dict)
        assert 'domain' in result
        assert result['domain'] == 'sports'
    
    def test_analyse_sport_with_model_score(self):
        """Analyse sport avec score ML."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        
        match_data = {
            'match_id': 'test_456',
            'home_team': {'name': 'Real Madrid'},
            'away_team': {'name': 'Barcelona'}
        }
        
        result = service.analyse_sport(match_data, model_score=0.75)
        
        assert isinstance(result, dict)
        assert 'ml_score' in result
        assert result['ml_score'] == 0.75
    
    def test_analyse_sport_fallback_has_required_fields(self):
        """Fallback sport a tous les champs requis."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        service.client = None  # Forcer le fallback
        
        result = service.analyse_sport({'match_id': 'test'})
        
        required_fields = [
            'domain', 'summary', 'analysis', 'prediction_type',
            'prediction_value', 'confidence', 'caveats', 'disclaimer'
        ]
        
        for field in required_fields:
            assert field in result


class TestGPTServiceAnalyseFinance:
    """Tests pour la méthode analyse_finance."""
    
    def test_analyse_finance_returns_dict(self):
        """Analyse finance retourne un dictionnaire."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        
        stock_data = {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'current_price': 150.0,
            'indicators': {'RSI': 55}
        }
        
        result = service.analyse_finance(stock_data)
        
        assert isinstance(result, dict)
        assert 'domain' in result
        assert result['domain'] == 'finance'
    
    def test_analyse_finance_with_model_score(self):
        """Analyse finance avec score ML."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        
        stock_data = {
            'symbol': 'GOOGL',
            'name': 'Alphabet',
            'sector': 'Technology'
        }
        
        result = service.analyse_finance(stock_data, model_score=0.65)
        
        assert isinstance(result, dict)
        assert 'ml_score' in result
        assert result['ml_score'] == 0.65
    
    def test_analyse_finance_fallback_has_required_fields(self):
        """Fallback finance a tous les champs requis."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        service.client = None  # Forcer le fallback
        
        result = service.analyse_finance({'symbol': 'TEST'})
        
        required_fields = [
            'domain', 'summary', 'analysis', 'prediction_type',
            'prediction_value', 'confidence', 'caveats', 'disclaimer'
        ]
        
        for field in required_fields:
            assert field in result


class TestGPTServicePromptCreation:
    """Tests pour la création de prompts."""
    
    def test_create_sports_prompt(self):
        """Créer un prompt sports."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        
        match_data = {'home_team': 'PSG', 'away_team': 'OM'}
        prompt = service._create_sports_prompt(match_data, None)
        
        assert isinstance(prompt, str)
        assert 'match' in prompt.lower() or 'sport' in prompt.lower()
    
    def test_create_sports_prompt_with_score(self):
        """Créer un prompt sports avec score."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        
        match_data = {'home_team': 'PSG', 'away_team': 'OM'}
        prompt = service._create_sports_prompt(match_data, 0.75)
        
        # Le format peut varier: 0.75, 75%, 75.00%
        assert '75' in prompt
    
    def test_create_finance_prompt(self):
        """Créer un prompt finance."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        
        stock_data = {'symbol': 'AAPL', 'current_price': 150}
        prompt = service._create_finance_prompt(stock_data, None)
        
        assert isinstance(prompt, str)
        assert 'AAPL' in prompt
    
    def test_create_finance_prompt_with_score(self):
        """Créer un prompt finance avec score."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        
        stock_data = {'symbol': 'AAPL', 'current_price': 150}
        prompt = service._create_finance_prompt(stock_data, 0.8)
        
        assert '0.8' in prompt


class TestGPTServiceSystemPrompt:
    """Tests pour le prompt système."""
    
    def test_get_system_prompt_returns_string(self):
        """Le prompt système est une chaîne."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        prompt = service._get_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_system_prompt_mentions_predictwise(self):
        """Le prompt mentionne PredictWise."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        prompt = service._get_system_prompt()
        
        assert 'PredictWise' in prompt


class TestGPTServiceFallback:
    """Tests pour les réponses fallback."""
    
    def test_fallback_response_sports(self):
        """Fallback sports a la bonne structure."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        result = service._get_fallback_response('sports')
        
        assert result['domain'] == 'sports'
        assert result['prediction_type'] == 'probability'
        assert result['prediction_value'] == 0.5
        assert result['confidence'] == 0.0
    
    def test_fallback_response_finance(self):
        """Fallback finance a la bonne structure."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        result = service._get_fallback_response('finance')
        
        assert result['domain'] == 'finance'
        assert result['prediction_type'] == 'trend'
        assert result['prediction_value'] == 'NEUTRAL'
        assert result['confidence'] == 0.0


class TestGPTServiceCallGPT:
    """Tests pour _call_gpt."""
    
    def test_call_gpt_without_client_returns_fallback(self):
        """Sans client, retourne fallback."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        service.client = None
        
        result = service._call_gpt("Test prompt", domain="sports")
        
        assert result['domain'] == 'sports'
        assert result['confidence'] == 0.0
    
    def test_call_gpt_handles_json_error(self):
        """Gère les erreurs JSON."""
        from app.services.gpt_service import GPTService
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Invalid JSON"))]
        
        service = GPTService()
        service.client = Mock()
        service.client.chat.completions.create.return_value = mock_response
        
        result = service._call_gpt("Test", domain="finance")
        
        # Doit retourner fallback car JSON invalide
        assert result['confidence'] == 0.0
    
    def test_call_gpt_handles_exception(self):
        """Gère les exceptions."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        service.client = Mock()
        service.client.chat.completions.create.side_effect = Exception("API Error")
        
        result = service._call_gpt("Test", domain="sports")
        
        # Doit retourner fallback
        assert result['domain'] == 'sports'
        assert result['confidence'] == 0.0
    
    def test_call_gpt_success_with_valid_json(self):
        """Succès avec JSON valide."""
        from app.services.gpt_service import GPTService
        
        valid_response = json.dumps({
            'domain': 'sports',
            'summary': 'Test summary',
            'analysis': 'Test analysis',
            'prediction_type': 'probability',
            'prediction_value': 0.7,
            'confidence': 0.8,
            'caveats': 'Test caveats',
            'disclaimer': 'Test disclaimer'
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=valid_response))]
        
        service = GPTService()
        service.client = Mock()
        service.client.chat.completions.create.return_value = mock_response
        
        result = service._call_gpt("Test", domain="sports")
        
        assert result['domain'] == 'sports'
        assert result['confidence'] == 0.8
        assert result['prediction_value'] == 0.7


class TestGPTServiceGlobalInstance:
    """Tests pour l'instance globale."""
    
    def test_global_instance_exists(self):
        """L'instance globale existe."""
        from app.services.gpt_service import gpt_service
        
        assert gpt_service is not None
    
    def test_global_instance_is_gpt_service(self):
        """L'instance globale est un GPTService."""
        from app.services.gpt_service import gpt_service, GPTService
        
        assert isinstance(gpt_service, GPTService)

