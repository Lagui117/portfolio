"""
Tests pour le service GPT/OpenAI.
"""

import pytest
import json
from unittest.mock import Mock, patch


class TestGPTService:
    """Tests pour GPTService."""
    
    def test_analyse_sport_fallback_mode(self, sample_match_data):
        """Analyse sportive en mode fallback."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        service.client = None
        
        result = service.analyse_sport(sample_match_data, 0.65)
        
        assert result['domain'] == 'sports'
        assert 'summary' in result
        assert 'educational_reminder' in result
    
    def test_analyse_finance_fallback_mode(self, sample_stock_data):
        """Analyse financiere en mode fallback."""
        from app.services.gpt_service import GPTService
        
        service = GPTService()
        service.client = None
        
        result = service.analyse_finance(sample_stock_data, 'UP')
        
        assert result['domain'] == 'finance'
        assert 'summary' in result
