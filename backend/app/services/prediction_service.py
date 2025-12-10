"""
Centralized prediction service.

This service provides a unified interface for all ML predictions across the application.
It handles model loading, feature preparation, and prediction execution.
"""
import os
import joblib
import numpy as np
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Model paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
ML_MODELS_DIR = os.path.join(BASE_DIR, 'ml', 'models')

SPORTS_MODEL_PATH = os.path.join(ML_MODELS_DIR, 'sports_model.pkl')
FINANCE_MODEL_PATH = os.path.join(ML_MODELS_DIR, 'finance_model.pkl')
FINANCE_SCALER_PATH = os.path.join(ML_MODELS_DIR, 'finance_scaler.pkl')


class PredictionService:
    """Centralized service for ML predictions."""
    
    def __init__(self):
        """Initialize prediction service."""
        self.sports_model = None
        self.finance_model = None
        self.finance_scaler = None
        self._load_models()
    
    def _load_models(self):
        """Load all ML models."""
        # Load sports model
        try:
            if os.path.exists(SPORTS_MODEL_PATH):
                self.sports_model = joblib.load(SPORTS_MODEL_PATH)
                logger.info(f"Sports model loaded successfully from {SPORTS_MODEL_PATH}")
            else:
                logger.warning(f"Sports model not found at {SPORTS_MODEL_PATH}")
        except Exception as e:
            logger.error(f"Error loading sports model: {e}")
        
        # Load finance model and scaler
        try:
            if os.path.exists(FINANCE_MODEL_PATH):
                self.finance_model = joblib.load(FINANCE_MODEL_PATH)
                logger.info(f"Finance model loaded successfully from {FINANCE_MODEL_PATH}")
            else:
                logger.warning(f"Finance model not found at {FINANCE_MODEL_PATH}")
            
            if os.path.exists(FINANCE_SCALER_PATH):
                self.finance_scaler = joblib.load(FINANCE_SCALER_PATH)
                logger.info(f"Finance scaler loaded successfully from {FINANCE_SCALER_PATH}")
            else:
                logger.warning(f"Finance scaler not found at {FINANCE_SCALER_PATH}")
        except Exception as e:
            logger.error(f"Error loading finance model: {e}")
    
    def predict_sport_event(
        self,
        home_stats: Dict[str, float],
        away_stats: Dict[str, float],
        odds: Optional[Dict[str, float]] = None,
        h2h_stats: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Predict outcome of a sports event.
        
        Args:
            home_stats: Home team statistics (win_rate, avg_goals_scored, recent_form)
            away_stats: Away team statistics (win_rate, avg_goals_scored, recent_form)
            odds: Betting odds (home, draw, away) - optional
            h2h_stats: Head-to-head statistics - optional
        
        Returns:
            Dictionary with prediction, probabilities, and confidence
        """
        if self.sports_model is None:
            return self._fallback_sports_prediction(home_stats, away_stats)
        
        try:
            # Prepare features
            features = self._prepare_sports_features(home_stats, away_stats, odds, h2h_stats)
            
            # Make prediction
            prediction = self.sports_model.predict([features])[0]
            probabilities = self.sports_model.predict_proba([features])[0]
            
            # Format probabilities
            classes = self.sports_model.classes_
            prob_dict = {cls: float(prob) for cls, prob in zip(classes, probabilities)}
            
            confidence = float(max(probabilities))
            
            return {
                'prediction': prediction,
                'probabilities': prob_dict,
                'confidence': confidence,
                'model_used': 'RandomForest',
                'features': features
            }
        
        except Exception as e:
            logger.error(f"Error in sports prediction: {e}")
            return self._fallback_sports_prediction(home_stats, away_stats)
    
    def _prepare_sports_features(
        self,
        home_stats: Dict[str, float],
        away_stats: Dict[str, float],
        odds: Optional[Dict[str, float]],
        h2h_stats: Optional[Dict[str, float]]
    ) -> List[float]:
        """Prepare feature vector for sports prediction."""
        # Basic stats
        home_win_rate = home_stats.get('win_rate', 0.5)
        home_avg_goals = home_stats.get('avg_goals_scored', 1.5)
        home_form = home_stats.get('recent_form', 1.5)
        
        away_win_rate = away_stats.get('win_rate', 0.5)
        away_avg_goals = away_stats.get('avg_goals_scored', 1.5)
        away_form = away_stats.get('recent_form', 1.5)
        
        # Derived features
        win_rate_diff = home_win_rate - away_win_rate
        form_diff = home_form - away_form
        
        # H2H stats
        h2h_home_win_rate = 0.33
        if h2h_stats:
            h2h_home_win_rate = h2h_stats.get('home_win_rate', 0.33)
        
        # Odds
        home_odds = 2.5
        draw_odds = 3.2
        away_odds = 2.8
        if odds:
            home_odds = odds.get('home', 2.5)
            draw_odds = odds.get('draw', 3.2)
            away_odds = odds.get('away', 2.8)
        
        odds_ratio = home_odds / away_odds if away_odds > 0 else 1.0
        
        return [
            home_win_rate,
            home_avg_goals,
            home_form,
            away_win_rate,
            away_avg_goals,
            away_form,
            win_rate_diff,
            form_diff,
            h2h_home_win_rate,
            home_odds,
            draw_odds,
            away_odds,
            odds_ratio
        ]
    
    def _fallback_sports_prediction(
        self,
        home_stats: Dict[str, float],
        away_stats: Dict[str, float]
    ) -> Dict[str, Any]:
        """Fallback prediction when model is not available."""
        home_strength = home_stats.get('win_rate', 0.5) + home_stats.get('recent_form', 1.5) / 3.0
        away_strength = away_stats.get('win_rate', 0.5) + away_stats.get('recent_form', 1.5) / 3.0
        
        total_strength = home_strength + away_strength
        if total_strength == 0:
            home_prob = 0.4
        else:
            home_prob = min(max(home_strength / total_strength, 0.2), 0.8)
        
        away_prob = min(max(away_strength / total_strength, 0.2), 0.8)
        draw_prob = max(0.1, 1.0 - home_prob - away_prob)
        
        # Normalize
        total = home_prob + draw_prob + away_prob
        home_prob /= total
        draw_prob /= total
        away_prob /= total
        
        # Determine prediction
        if home_prob > draw_prob and home_prob > away_prob:
            prediction = 'HOME_WIN'
            confidence = home_prob
        elif away_prob > draw_prob:
            prediction = 'AWAY_WIN'
            confidence = away_prob
        else:
            prediction = 'DRAW'
            confidence = draw_prob
        
        return {
            'prediction': prediction,
            'probabilities': {
                'HOME_WIN': float(home_prob),
                'DRAW': float(draw_prob),
                'AWAY_WIN': float(away_prob)
            },
            'confidence': float(confidence),
            'model_used': 'Fallback',
            'features': None
        }
    
    def predict_stock_movement(
        self,
        technical_indicators: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Predict stock price movement.
        
        Args:
            technical_indicators: Dictionary with MA, RSI, MACD, volatility, price changes
        
        Returns:
            Dictionary with prediction, probabilities, and confidence
        """
        if self.finance_model is None or self.finance_scaler is None:
            return self._fallback_finance_prediction(technical_indicators)
        
        try:
            # Prepare features
            features = self._prepare_finance_features(technical_indicators)
            
            # Scale features
            features_scaled = self.finance_scaler.transform([features])
            
            # Make prediction
            prediction = self.finance_model.predict(features_scaled)[0]
            probabilities = self.finance_model.predict_proba(features_scaled)[0]
            
            # Format probabilities
            classes = self.finance_model.classes_
            prob_dict = {cls: float(prob) for cls, prob in zip(classes, probabilities)}
            
            confidence = float(max(probabilities))
            
            return {
                'prediction': prediction,
                'probabilities': prob_dict,
                'confidence': confidence,
                'model_used': 'LogisticRegression',
                'features': features
            }
        
        except Exception as e:
            logger.error(f"Error in finance prediction: {e}")
            return self._fallback_finance_prediction(technical_indicators)
    
    def _prepare_finance_features(self, indicators: Dict[str, float]) -> List[float]:
        """Prepare feature vector for finance prediction."""
        # Extract indicators
        ma_5 = indicators.get('MA_5', 100.0)
        ma_20 = indicators.get('MA_20', 100.0)
        ma_50 = indicators.get('MA_50', 100.0)
        rsi = indicators.get('RSI', 50.0)
        macd = indicators.get('MACD', 0.0)
        volatility_daily = indicators.get('volatility_daily', 0.02)
        volatility_annual = indicators.get('volatility_annual', 0.3)
        price_change_1d = indicators.get('price_change_1d', 0.0)
        price_change_5d = indicators.get('price_change_5d', 0.0)
        price_change_20d = indicators.get('price_change_20d', 0.0)
        current_price = indicators.get('current_price', 100.0)
        
        # Derived features
        ma5_minus_ma20 = ma_5 - ma_20
        ma20_minus_ma50 = ma_20 - ma_50
        ma5_ratio = ma_5 / current_price if current_price > 0 else 1.0
        ma20_ratio = ma_20 / current_price if current_price > 0 else 1.0
        
        return [
            ma_5,
            ma_20,
            ma_50,
            rsi,
            macd,
            volatility_daily,
            volatility_annual,
            price_change_1d,
            price_change_5d,
            price_change_20d,
            ma5_minus_ma20,
            ma20_minus_ma50,
            ma5_ratio,
            ma20_ratio
        ]
    
    def _fallback_finance_prediction(
        self,
        indicators: Dict[str, float]
    ) -> Dict[str, Any]:
        """Fallback prediction when model is not available."""
        # Simple rule-based prediction
        score = 0
        
        # RSI signal
        rsi = indicators.get('RSI', 50.0)
        if rsi > 70:
            score -= 1  # Overbought
        elif rsi < 30:
            score += 1  # Oversold
        
        # MACD signal
        macd = indicators.get('MACD', 0.0)
        if macd > 0:
            score += 1
        else:
            score -= 1
        
        # Moving averages
        ma_5 = indicators.get('MA_5', 100.0)
        ma_20 = indicators.get('MA_20', 100.0)
        if ma_5 > ma_20:
            score += 1
        else:
            score -= 1
        
        # Recent momentum
        chg_5d = indicators.get('price_change_5d', 0.0)
        if chg_5d > 0.02:
            score += 1
        elif chg_5d < -0.02:
            score -= 1
        
        # Determine prediction
        if score > 0:
            prediction = 'UP'
            up_prob = min(0.5 + score * 0.1, 0.8)
            down_prob = 1.0 - up_prob
        else:
            prediction = 'DOWN'
            down_prob = min(0.5 + abs(score) * 0.1, 0.8)
            up_prob = 1.0 - down_prob
        
        confidence = max(up_prob, down_prob)
        
        return {
            'prediction': prediction,
            'probabilities': {
                'UP': float(up_prob),
                'DOWN': float(down_prob)
            },
            'confidence': float(confidence),
            'model_used': 'Fallback',
            'features': None
        }
    
    def get_models_info(self) -> Dict[str, Any]:
        """Get information about loaded models."""
        return {
            'sports_model': {
                'loaded': self.sports_model is not None,
                'type': type(self.sports_model).__name__ if self.sports_model else None,
                'path': SPORTS_MODEL_PATH
            },
            'finance_model': {
                'loaded': self.finance_model is not None,
                'type': type(self.finance_model).__name__ if self.finance_model else None,
                'path': FINANCE_MODEL_PATH
            },
            'finance_scaler': {
                'loaded': self.finance_scaler is not None,
                'type': type(self.finance_scaler).__name__ if self.finance_scaler else None,
                'path': FINANCE_SCALER_PATH
            }
        }


# Global instance
_prediction_service = None


def get_prediction_service() -> PredictionService:
    """Get the singleton prediction service instance."""
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService()
    return _prediction_service
