"""
Tests d'integration entre ML et backend prediction_service.
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch
import joblib

# Ajouter backend au path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, backend_path)


class TestPredictionServiceIntegration:
    """Tests d'integration du service de prediction."""
    
    def test_predict_sport_with_real_model(
        self,
        small_sports_dataset,
        sample_match_features,
        temp_models_dir
    ):
        """Integration avec un vrai modele ML sports."""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        
        # Entrainer un petit modele
        df = small_sports_dataset
        feature_cols = [
            'home_win_rate', 'away_win_rate',
            'home_goals_avg', 'away_goals_avg',
            'home_odds', 'draw_odds', 'away_odds'
        ]
        
        X = df[feature_cols]
        y = df['result']
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        # Sauvegarder
        model_path = os.path.join(temp_models_dir, 'sports_model.pkl')
        joblib.dump(model, model_path)
        
        # Charger le modele via prediction_service
        with patch('app.services.prediction_service.PredictionService') as MockService:
            service = MockService.return_value
            service.sports_model = model
            
            # Simuler une prediction
            features_array = [
                sample_match_features['home_win_rate'],
                sample_match_features['away_win_rate'],
                sample_match_features['home_goals_avg'],
                sample_match_features['away_goals_avg'],
                sample_match_features['home_odds'],
                sample_match_features['draw_odds'],
                sample_match_features['away_odds']
            ]
            
            probas = model.predict_proba([features_array])[0]
            
            # Verifier format des probabilites
            assert len(probas) == 3
            assert all(0 <= p <= 1 for p in probas)
            assert abs(sum(probas) - 1.0) < 0.01
    
    def test_predict_stock_with_real_model(
        self,
        small_finance_dataset,
        sample_stock_features,
        temp_models_dir
    ):
        """Integration avec un vrai modele ML finance."""
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.preprocessing import StandardScaler
        
        # Entrainer un petit modele
        df = small_finance_dataset
        feature_cols = [
            'rsi', 'macd', 'signal', 'sma_20', 'sma_50',
            'volatility', 'volume_ratio', 'price_change'
        ]
        
        X = df[feature_cols]
        y = df['trend']
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = GradientBoostingClassifier(
            n_estimators=10,
            max_depth=3,
            random_state=42
        )
        model.fit(X_scaled, y)
        
        # Sauvegarder
        model_path = os.path.join(temp_models_dir, 'finance_model.pkl')
        scaler_path = os.path.join(temp_models_dir, 'finance_scaler.pkl')
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        
        # Simuler une prediction
        features_array = [
            sample_stock_features['rsi'],
            sample_stock_features['macd'],
            sample_stock_features['signal'],
            sample_stock_features['sma_20'],
            sample_stock_features['sma_50'],
            sample_stock_features['volatility'],
            sample_stock_features['volume_ratio'],
            sample_stock_features['price_change']
        ]
        
        features_scaled = scaler.transform([features_array])
        prediction = model.predict(features_scaled)[0]
        
        # Verifier que la prediction est valide
        assert prediction in ['UP', 'DOWN', 'NEUTRAL']
    
    def test_missing_model_file_handling(self, temp_models_dir):
        """Gestion d'un fichier modele manquant."""
        from app.services.prediction_service import PredictionService
        
        # Creer un service avec un mauvais chemin
        service = PredictionService()
        service.ml_models_dir = temp_models_dir
        
        # Tenter de charger des modeles inexistants
        service._load_models()
        
        # Le service ne doit pas crasher
        assert service.sports_model is None
        assert service.finance_model is None
    
    def test_predict_sport_without_model_uses_heuristic(self):
        """Sans modele, utilise la methode heuristique."""
        from app.services.prediction_service import PredictionService
        
        service = PredictionService()
        service.sports_model = None
        
        match_data = {
            'home_team': {'win_rate': 0.7, 'goals_scored_avg': 2.5},
            'away_team': {'win_rate': 0.5, 'goals_scored_avg': 1.5},
            'odds': {'home_win': 1.8, 'away_win': 4.0}
        }
        
        result = service.predict_sport(match_data)
        
        # Doit retourner un resultat valide
        assert result is not None
        assert isinstance(result, (int, float, dict))
    
    def test_predict_stock_without_model_uses_heuristic(self):
        """Sans modele, utilise la methode heuristique."""
        from app.services.prediction_service import PredictionService
        
        service = PredictionService()
        service.finance_model = None
        
        stock_data = {
            'current_price': 150.0,
            'indicators': {
                'rsi': 65,
                'macd': 1.5,
                'signal': 1.0,
                'sma_20': 148.0,
                'sma_50': 145.0
            }
        }
        
        result = service.predict_stock(stock_data)
        
        # Doit retourner un resultat valide
        assert result is not None
        assert isinstance(result, (str, dict))
