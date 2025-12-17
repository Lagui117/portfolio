"""
Tests for ML prediction service.

Validates integration with backend service layer.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, backend_dir)

from app.services.ml_prediction_service import MLPredictionService


class TestMLPredictionService(unittest.TestCase):
    """Test cases for MLPredictionService."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create service with mock models directory
        self.test_models_dir = "/tmp/test_models"
        
        # Mock model loading
        with patch.object(MLPredictionService, '_load_models'):
            self.service = MLPredictionService(models_dir=self.test_models_dir)
    
    def test_initialization(self):
        """Test service initializes correctly."""
        self.assertIsNotNone(self.service)
        self.assertEqual(self.service.models_dir, self.test_models_dir)
        self.assertIsNotNone(self.service.sports_extractor)
        self.assertIsNotNone(self.service.finance_extractor)
    
    def test_fallback_sports_prediction(self):
        """Test sports fallback when model not loaded."""
        # No model loaded
        self.service.sports_model = None
        
        match_data = {
            'home_form': [2, 1, 2],
            'away_form': [1, 0, 1],
            'home_attack': 75.0,
            'away_attack': 70.0,
            'home_defense': 80.0,
            'away_defense': 75.0,
        }
        
        result = self.service.predict_sport(match_data)
        
        # Should return fallback
        self.assertEqual(result['model_type'], 'fallback')
        self.assertIn('home_win_probability', result)
        self.assertIn('draw_probability', result)
        self.assertIn('away_win_probability', result)
        self.assertIn('confidence', result)
        
        # Probabilities should sum to ~1.0
        total = (
            result['home_win_probability'] +
            result['draw_probability'] +
            result['away_win_probability']
        )
        self.assertAlmostEqual(total, 1.0, places=1)
    
    def test_fallback_finance_prediction(self):
        """Test finance fallback when model not loaded."""
        # No model loaded
        self.service.finance_model = None
        
        asset_data = {
            'price_history': list(range(100, 160)),
            'volume_history': [5000] * 60
        }
        
        result = self.service.predict_finance(asset_data)
        
        # Should return fallback
        self.assertEqual(result['model_type'], 'fallback')
        self.assertIn('trend_prediction', result)
        self.assertIn('up_probability', result)
        self.assertIn('confidence', result)
        
        # Should predict NEUTRAL in fallback
        self.assertEqual(result['trend_prediction'], 'NEUTRAL')
    
    def test_sports_prediction_with_model(self):
        """Test sports prediction with loaded model."""
        # Mock model
        mock_model = Mock()
        mock_model.predict_proba.return_value = np.array([[0.5, 0.3, 0.2]])
        self.service.sports_model = mock_model
        
        # Mock scaler
        mock_scaler = Mock()
        mock_scaler.transform.return_value = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]])
        self.service.sports_scaler = mock_scaler
        
        match_data = {
            'home_form': [2, 1, 2, 1, 2],
            'away_form': [1, 0, 1, 2, 0],
            'home_attack': 75.5,
            'away_attack': 68.2,
            'home_defense': 82.0,
            'away_defense': 78.5,
            'home_goals_scored': 15,
            'away_goals_scored': 12,
            'home_goals_conceded': 8,
            'away_goals_conceded': 10,
            'home_win_rate': 0.65,
            'away_win_rate': 0.50,
            'is_home': True,
            'home_xg': [1.8, 2.1, 1.5, 2.3, 1.9],
            'away_xg': [1.2, 1.5, 1.8, 1.0, 1.6],
            'h2h_history': [1, 1, 0, 1, 2],
            'home_rest_days': 3,
            'away_rest_days': 2
        }
        
        result = self.service.predict_sport(match_data)
        
        # Should call model
        mock_model.predict_proba.assert_called_once()
        
        # Should return probabilities
        self.assertEqual(result['home_win_probability'], 0.5)
        self.assertEqual(result['draw_probability'], 0.3)
        self.assertEqual(result['away_win_probability'], 0.2)
        self.assertEqual(result['confidence'], 0.5)
    
    def test_finance_prediction_with_model(self):
        """Test finance prediction with loaded model."""
        # Mock model
        mock_model = Mock()
        mock_model.predict_proba.return_value = np.array([[0.6, 0.2, 0.2]])
        self.service.finance_model = mock_model
        
        # Mock scaler
        mock_scaler = Mock()
        mock_scaler.transform.return_value = np.random.randn(1, 14)
        self.service.finance_scaler = mock_scaler
        
        asset_data = {
            'price_history': list(range(100, 160)),
            'volume_history': [5000] * 60
        }
        
        result = self.service.predict_finance(asset_data)
        
        # Should call model
        mock_model.predict_proba.assert_called_once()
        
        # Should return trend prediction
        self.assertEqual(result['trend_prediction'], 'UP')
        self.assertEqual(result['up_probability'], 0.6)
        self.assertEqual(result['confidence'], 0.6)
    
    def test_get_model_info(self):
        """Test model info retrieval."""
        # Set mock models
        self.service.sports_model = Mock()
        self.service.finance_model = None
        
        info = self.service.get_model_info()
        
        # Should report model status
        self.assertTrue(info['sports_model_loaded'])
        self.assertFalse(info['finance_model_loaded'])
        self.assertEqual(info['models_directory'], self.test_models_dir)
    
    def test_sports_prediction_handles_errors(self):
        """Test sports prediction error handling."""
        # Mock model that raises exception
        mock_model = Mock()
        mock_model.predict_proba.side_effect = Exception("Model error")
        self.service.sports_model = mock_model
        
        match_data = {
            'home_form': [2, 1, 2, 1, 2],
            'away_form': [1, 0, 1, 2, 0],
            'home_attack': 75.5,
            'away_attack': 68.2,
            'home_defense': 82.0,
            'away_defense': 78.5,
            'home_goals_scored': 15,
            'away_goals_scored': 12,
            'home_goals_conceded': 8,
            'away_goals_conceded': 10,
            'home_win_rate': 0.65,
            'away_win_rate': 0.50,
            'is_home': True,
            'home_xg': [1.8, 2.1, 1.5, 2.3, 1.9],
            'away_xg': [1.2, 1.5, 1.8, 1.0, 1.6],
            'h2h_history': [1, 1, 0, 1, 2],
            'home_rest_days': 3,
            'away_rest_days': 2
        }
        
        result = self.service.predict_sport(match_data)
        
        # Should return fallback on error
        self.assertEqual(result['model_type'], 'fallback')
        self.assertLess(result['confidence'], 0.5)
    
    def test_finance_prediction_handles_insufficient_data(self):
        """Test finance prediction with insufficient data."""
        # Set model
        self.service.finance_model = Mock()
        
        # Insufficient price history
        asset_data = {
            'price_history': [100, 101, 102],
            'volume_history': [1000, 1100, 1200]
        }
        
        result = self.service.predict_finance(asset_data)
        
        # Should return fallback
        self.assertEqual(result['model_type'], 'fallback')


if __name__ == '__main__':
    unittest.main()
