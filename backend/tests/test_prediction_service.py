"""
Tests unitaires pour le service de prediction.
"""

import pytest


class TestPredictionService:
    """Tests pour le service de prediction."""
    
    def test_prediction_service_import(self):
        """Test import du service."""
        from app.services.prediction_service import prediction_service
        assert prediction_service is not None
    
    def test_predict_sport_basic(self, app):
        """Test prediction sports basique."""
        with app.app_context():
            from app.services.prediction_service import PredictionService
            
            service = PredictionService()
            
            match_data = {
                'home_team': {'win_rate': 0.7, 'goals_scored_avg': 2.0},
                'away_team': {'win_rate': 0.5, 'goals_scored_avg': 1.5},
                'odds': {'home_win': 2.0, 'draw': 3.5, 'away_win': 3.0}
            }
            
            score = service.predict_sport(match_data)
            
            assert score is not None
            assert 0 <= score <= 1
    
    def test_predict_sport_home_favorite(self, app):
        """Test prediction avec equipe domicile favorite."""
        with app.app_context():
            from app.services.prediction_service import PredictionService
            
            service = PredictionService()
            
            match_data = {
                'home_team': {'win_rate': 0.9, 'goals_scored_avg': 3.0},
                'away_team': {'win_rate': 0.3, 'goals_scored_avg': 1.0},
                'odds': {'home_win': 1.5, 'draw': 4.0, 'away_win': 5.0}
            }
            
            score = service.predict_sport(match_data)
            
            # L'equipe domicile devrait avoir un score > 0.5
            assert score > 0.5
    
    def test_predict_sport_away_favorite(self, app):
        """Test prediction avec equipe exterieur favorite."""
        with app.app_context():
            from app.services.prediction_service import PredictionService
            
            service = PredictionService()
            
            match_data = {
                'home_team': {'win_rate': 0.3, 'goals_scored_avg': 1.0},
                'away_team': {'win_rate': 0.9, 'goals_scored_avg': 3.0},
                'odds': {'home_win': 5.0, 'draw': 4.0, 'away_win': 1.5}
            }
            
            score = service.predict_sport(match_data)
            
            # L'equipe domicile devrait avoir un score < 0.5
            assert score < 0.5
    
    def test_predict_sport_equal_teams(self, app):
        """Test prediction avec equipes equilibrees."""
        with app.app_context():
            from app.services.prediction_service import PredictionService
            
            service = PredictionService()
            
            match_data = {
                'home_team': {'win_rate': 0.5, 'goals_scored_avg': 1.5},
                'away_team': {'win_rate': 0.5, 'goals_scored_avg': 1.5},
                'odds': {'home_win': 2.5, 'draw': 3.3, 'away_win': 2.5}
            }
            
            score = service.predict_sport(match_data)
            
            # Score proche de 0.5
            assert 0.3 <= score <= 0.7
    
    def test_predict_sport_missing_data(self, app):
        """Test prediction avec donnees manquantes."""
        with app.app_context():
            from app.services.prediction_service import PredictionService
            
            service = PredictionService()
            
            match_data = {
                'home_team': {},
                'away_team': {}
            }
            
            score = service.predict_sport(match_data)
            
            # Devrait retourner une valeur par defaut
            assert score is not None
            assert 0 <= score <= 1
    
    def test_predict_stock_basic(self, app):
        """Test prediction finance basique."""
        with app.app_context():
            from app.services.prediction_service import PredictionService
            
            service = PredictionService()
            
            stock_data = {
                'current_price': 175.0,
                'indicators': {
                    'RSI': 55,
                    'MA_5': 173,
                    'MA_20': 170,
                    'volatility_daily': 0.02
                }
            }
            
            score = service.predict_stock(stock_data)
            
            assert score is not None
            assert -1 <= score <= 1
    
    def test_predict_stock_oversold(self, app):
        """Test prediction avec RSI survendu."""
        with app.app_context():
            from app.services.prediction_service import PredictionService
            
            service = PredictionService()
            
            stock_data = {
                'current_price': 175.0,
                'indicators': {
                    'RSI': 25,  # Survendu
                    'MA_5': 180,
                    'MA_20': 185
                }
            }
            
            score = service.predict_stock(stock_data)
            
            # RSI bas devrait donner un signal positif
            assert score > 0
    
    def test_predict_stock_overbought(self, app):
        """Test prediction avec RSI surachete."""
        with app.app_context():
            from app.services.prediction_service import PredictionService
            
            service = PredictionService()
            
            stock_data = {
                'current_price': 175.0,
                'indicators': {
                    'RSI': 80,  # Surachete
                    'MA_5': 170,
                    'MA_20': 165
                }
            }
            
            score = service.predict_stock(stock_data)
            
            # RSI haut devrait donner un signal negatif
            assert score < 0
    
    def test_predict_stock_missing_data(self, app):
        """Test prediction finance avec donnees manquantes."""
        with app.app_context():
            from app.services.prediction_service import PredictionService
            
            service = PredictionService()
            
            stock_data = {
                'current_price': 100,
                'indicators': {}
            }
            
            score = service.predict_stock(stock_data)
            
            assert score is not None
            assert -1 <= score <= 1
