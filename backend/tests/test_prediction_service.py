"""
Tests pour le service de prediction ML.
"""

import pytest
from unittest.mock import Mock, patch


class TestPredictionService:
    """Tests pour PredictionService."""
    
    def test_predict_sport_with_model(self, sample_match_data):
        """Prediction sports avec modele ML charge."""
        from app.services.prediction_service import PredictionService
        
        service = PredictionService()
        
        # Mock du modele
        mock_model = Mock()
        mock_model.predict_proba.return_value = [[0.68, 0.22, 0.10]]
        service.sports_model = mock_model
        
        result = service.predict_sport(sample_match_data)
        
        assert isinstance(result, (int, float, dict))
    
    def test_predict_sport_without_model(self, sample_match_data):
        """Prediction sports avec heuristique."""
        from app.services.prediction_service import PredictionService
        
        service = PredictionService()
        service.sports_model = None
        
        result = service.predict_sport(sample_match_data)
        
        assert result is not None
    
    def test_predict_stock_without_model(self, sample_stock_data):
        """Prediction finance avec heuristique."""
        from app.services.prediction_service import PredictionService
        
        service = PredictionService()
        service.finance_model = None
        
        result = service.predict_stock(sample_stock_data)
        
        assert result is not None
