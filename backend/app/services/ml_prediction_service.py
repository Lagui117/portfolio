"""
ML Prediction Service

Integrates trained ML models for sports and finance predictions.
Handles model loading, feature extraction, and prediction generation.
"""

import os
import pickle
import numpy as np
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import feature extractors and exceptions
import sys
ml_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ml')
sys.path.append(ml_path)

from features.sports_features import SportsFeatureExtractor
from features.finance_features import FinanceFeatureExtractor
from utils.exceptions import ModelNotLoadedError, MissingFeatureError, InsufficientDataError
from utils.validation import validate_sports_data, validate_finance_data


class MLPredictionService:
    """
    Service for loading ML models and generating predictions.
    
    Handles:
    - Model loading and caching
    - Feature extraction
    - Prediction generation
    - Error handling and fallbacks
    """
    
    def __init__(self, models_dir: Optional[str] = None):
        """
        Initialize the prediction service.
        
        Args:
            models_dir: Directory containing model files (.pkl)
        """
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'ml', 'models')
        
        self.models_dir = models_dir
        
        # Model storage
        self.sports_model = None
        self.sports_scaler = None
        self.finance_model = None
        self.finance_scaler = None
        
        # Feature extractors
        self.sports_extractor = SportsFeatureExtractor()
        self.finance_extractor = FinanceFeatureExtractor()
        
        # Load models on initialization
        self._load_models()
    
    def _load_models(self):
        """Load all ML models and scalers from disk."""
        try:
            # Sports model
            sports_model_path = os.path.join(self.models_dir, 'sports_model.pkl')
            sports_scaler_path = os.path.join(self.models_dir, 'sports_scaler.pkl')
            
            if os.path.exists(sports_model_path):
                with open(sports_model_path, 'rb') as f:
                    self.sports_model = pickle.load(f)
                logger.info("Sports model loaded successfully")
            else:
                logger.warning(f"Sports model not found at {sports_model_path}")
            
            if os.path.exists(sports_scaler_path):
                with open(sports_scaler_path, 'rb') as f:
                    self.sports_scaler = pickle.load(f)
                logger.info("Sports scaler loaded successfully")
            
            # Finance model
            finance_model_path = os.path.join(self.models_dir, 'finance_model.pkl')
            finance_scaler_path = os.path.join(self.models_dir, 'finance_scaler.pkl')
            
            if os.path.exists(finance_model_path):
                with open(finance_model_path, 'rb') as f:
                    self.finance_model = pickle.load(f)
                logger.info("Finance model loaded successfully")
            else:
                logger.warning(f"Finance model not found at {finance_model_path}")
            
            if os.path.exists(finance_scaler_path):
                with open(finance_scaler_path, 'rb') as f:
                    self.finance_scaler = pickle.load(f)
                logger.info("Finance scaler loaded successfully")
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def predict_sport(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict sports match outcome.
        
        Args:
            match_data: Dictionary with match statistics
            
        Returns:
            Dictionary with prediction results:
            {
                "home_win_probability": float,
                "draw_probability": float,
                "away_win_probability": float,
                "confidence": float,
                "model_type": str
            }
            
        Raises:
            ModelNotLoadedError: If sports model is not loaded
            MissingFeatureError: If required features are missing
        """
        if self.sports_model is None:
            logger.warning("Sports model not loaded, using fallback")
            return self._fallback_sports_prediction()
        
        try:
            # Validate input data
            validated_data = validate_sports_data(
                match_data,
                self.sports_extractor.REQUIRED_FEATURES
            )
            
            # Extract features
            features = self.sports_extractor.extract(validated_data)
            
            # Scale features
            if self.sports_scaler is not None:
                features_scaled = self.sports_scaler.transform(features)
            else:
                features_scaled = features
            
            # Get prediction probabilities
            probabilities = self.sports_model.predict_proba(features_scaled)[0]
            
            # Map to outcome classes (0: Home, 1: Draw, 2: Away)
            home_win_prob = float(probabilities[0])
            draw_prob = float(probabilities[1])
            away_win_prob = float(probabilities[2])
            
            # Confidence is the maximum probability
            confidence = float(max(probabilities))
            
            result = {
                "home_win_probability": home_win_prob,
                "draw_probability": draw_prob,
                "away_win_probability": away_win_prob,
                "confidence": confidence,
                "model_type": type(self.sports_model).__name__
            }
            
            logger.info(f"Sports prediction generated: {result}")
            return result
            
        except (MissingFeatureError, InsufficientDataError) as e:
            logger.warning(f"Validation error in sports prediction: {e}")
            return self._fallback_sports_prediction(confidence=0.3)
        
        except Exception as e:
            logger.error(f"Error in sports prediction: {e}")
            return self._fallback_sports_prediction(confidence=0.2)
    
    def predict_finance(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict financial asset trend.
        
        Args:
            asset_data: Dictionary with price history and volume
            
        Returns:
            Dictionary with prediction results:
            {
                "trend_prediction": "UP"|"DOWN"|"NEUTRAL",
                "up_probability": float,
                "confidence": float,
                "model_type": str
            }
            
        Raises:
            ModelNotLoadedError: If finance model is not loaded
            InsufficientDataError: If insufficient price history
        """
        if self.finance_model is None:
            logger.warning("Finance model not loaded, using fallback")
            return self._fallback_finance_prediction()
        
        try:
            # Validate input data
            validated_data = validate_finance_data(
                asset_data,
                minimum_history=self.finance_extractor.MINIMUM_HISTORY
            )
            
            # Extract features
            features = self.finance_extractor.extract(validated_data)
            
            # Scale features
            if self.finance_scaler is not None:
                features_scaled = self.finance_scaler.transform(features)
            else:
                features_scaled = features
            
            # Get prediction probabilities
            probabilities = self.finance_model.predict_proba(features_scaled)[0]
            
            # Map to trend classes (0: UP, 1: NEUTRAL, 2: DOWN)
            up_prob = float(probabilities[0])
            neutral_prob = float(probabilities[1])
            down_prob = float(probabilities[2])
            
            # Determine trend
            predicted_class = np.argmax(probabilities)
            trend_map = {0: "UP", 1: "NEUTRAL", 2: "DOWN"}
            trend = trend_map[predicted_class]
            
            # Confidence is the maximum probability
            confidence = float(max(probabilities))
            
            result = {
                "trend_prediction": trend,
                "up_probability": up_prob,
                "neutral_probability": neutral_prob,
                "down_probability": down_prob,
                "confidence": confidence,
                "model_type": type(self.finance_model).__name__
            }
            
            logger.info(f"Finance prediction generated: {result}")
            return result
            
        except (InsufficientDataError, MissingFeatureError) as e:
            logger.warning(f"Validation error in finance prediction: {e}")
            return self._fallback_finance_prediction(confidence=0.3)
        
        except Exception as e:
            logger.error(f"Error in finance prediction: {e}")
            return self._fallback_finance_prediction(confidence=0.2)
    
    def _fallback_sports_prediction(self, confidence: float = 0.5) -> Dict[str, Any]:
        """
        Generate fallback prediction for sports when model fails.
        
        Returns balanced probabilities with low confidence.
        """
        return {
            "home_win_probability": 0.40,
            "draw_probability": 0.30,
            "away_win_probability": 0.30,
            "confidence": confidence,
            "model_type": "fallback"
        }
    
    def _fallback_finance_prediction(self, confidence: float = 0.5) -> Dict[str, Any]:
        """
        Generate fallback prediction for finance when model fails.
        
        Returns neutral trend with low confidence.
        """
        return {
            "trend_prediction": "NEUTRAL",
            "up_probability": 0.33,
            "neutral_probability": 0.34,
            "down_probability": 0.33,
            "confidence": confidence,
            "model_type": "fallback"
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about loaded models.
        
        Returns:
            Dictionary with model status and types
        """
        return {
            "sports_model_loaded": self.sports_model is not None,
            "sports_model_type": type(self.sports_model).__name__ if self.sports_model else None,
            "finance_model_loaded": self.finance_model is not None,
            "finance_model_type": type(self.finance_model).__name__ if self.finance_model else None,
            "models_directory": self.models_dir
        }


# Global service instance
_prediction_service = None


def get_prediction_service() -> MLPredictionService:
    """
    Get or create the global prediction service instance.
    
    Returns:
        MLPredictionService instance
    """
    global _prediction_service
    
    if _prediction_service is None:
        _prediction_service = MLPredictionService()
    
    return _prediction_service
