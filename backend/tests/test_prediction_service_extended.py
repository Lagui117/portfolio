"""
Tests étendus pour PredictionService.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.prediction_service import PredictionService


class TestPredictionServiceInit:
    """Tests pour l'initialisation du service."""
    
    def test_init_without_models(self):
        """Service fonctionne sans modèles ML."""
        service = PredictionService()
        
        # Doit s'initialiser même sans modèles
        assert hasattr(service, 'sports_model')
        assert hasattr(service, 'finance_model')
    
    def test_models_dir_configured(self):
        """Le répertoire des modèles est configuré."""
        service = PredictionService()
        
        assert hasattr(service, 'ml_models_dir')
        assert service.ml_models_dir is not None


class TestPredictionServiceSports:
    """Tests pour les prédictions sportives."""
    
    def test_predict_sport_balanced_teams(self):
        """Équipes équilibrées donnent ~50%."""
        service = PredictionService()
        
        match_data = {
            'home_team': {'win_rate': 0.5, 'goals_scored_avg': 1.5},
            'away_team': {'win_rate': 0.5, 'goals_scored_avg': 1.5},
            'odds': {'home_win': 2.5, 'draw': 3.0, 'away_win': 2.5}
        }
        
        score = service.predict_sport(match_data)
        
        assert 0.35 <= score <= 0.65  # Proche de 50%
    
    def test_predict_sport_home_favorite(self):
        """Équipe domicile favorite donne score > 0.5."""
        service = PredictionService()
        
        match_data = {
            'home_team': {'win_rate': 0.8, 'goals_scored_avg': 2.5},
            'away_team': {'win_rate': 0.3, 'goals_scored_avg': 0.8},
            'odds': {'home_win': 1.3, 'draw': 4.5, 'away_win': 8.0}
        }
        
        score = service.predict_sport(match_data)
        
        assert score > 0.5
    
    def test_predict_sport_away_favorite(self):
        """Équipe extérieure favorite donne score < 0.5."""
        service = PredictionService()
        
        match_data = {
            'home_team': {'win_rate': 0.3, 'goals_scored_avg': 0.8},
            'away_team': {'win_rate': 0.8, 'goals_scored_avg': 2.5},
            'odds': {'home_win': 8.0, 'draw': 4.5, 'away_win': 1.3}
        }
        
        score = service.predict_sport(match_data)
        
        assert score < 0.5
    
    def test_predict_sport_bounded_score(self):
        """Score toujours entre 0.1 et 0.9."""
        service = PredictionService()
        
        # Cas extrême
        match_data = {
            'home_team': {'win_rate': 1.0, 'goals_scored_avg': 5.0},
            'away_team': {'win_rate': 0.0, 'goals_scored_avg': 0.0},
            'odds': {'home_win': 1.01, 'draw': 50.0, 'away_win': 100.0}
        }
        
        score = service.predict_sport(match_data)
        
        assert 0.1 <= score <= 0.9
    
    def test_predict_sport_missing_data(self):
        """Gère les données manquantes."""
        service = PredictionService()
        
        # Données minimales
        match_data = {}
        
        score = service.predict_sport(match_data)
        
        assert 0 <= score <= 1
    
    def test_predict_sport_partial_data(self):
        """Gère les données partielles."""
        service = PredictionService()
        
        match_data = {
            'home_team': {'win_rate': 0.6},
            'away_team': {}
        }
        
        score = service.predict_sport(match_data)
        
        assert 0 <= score <= 1
    
    def test_predict_sport_invalid_values(self):
        """Gère les valeurs invalides."""
        service = PredictionService()
        
        match_data = {
            'home_team': {'win_rate': 'invalid', 'goals_scored_avg': None},
            'away_team': {'win_rate': -1, 'goals_scored_avg': 'abc'},
            'odds': {'home_win': 'bad', 'draw': 0, 'away_win': -5}
        }
        
        # Ne doit pas lever d'exception
        score = service.predict_sport(match_data)
        
        assert 0 <= score <= 1


class TestPredictionServiceFinance:
    """Tests pour les prédictions financières."""
    
    def test_predict_stock_neutral(self):
        """RSI neutre donne score proche de 0."""
        service = PredictionService()
        
        stock_data = {
            'current_price': 100.0,
            'price_change_pct': 0,
            'indicators': {
                'RSI': 50,
                'MA_5': 100.0,
                'MA_20': 100.0,
                'volatility_daily': 0.02
            }
        }
        
        score = service.predict_stock(stock_data)
        
        assert -0.3 <= score <= 0.3  # Proche de neutre
    
    def test_predict_stock_oversold(self):
        """RSI survendu donne signal haussier."""
        service = PredictionService()
        
        stock_data = {
            'current_price': 100.0,
            'indicators': {
                'RSI': 20,  # Très survendu
                'MA_5': 98.0,
                'MA_20': 95.0,
                'volatility_daily': 0.02
            }
        }
        
        score = service.predict_stock(stock_data)
        
        assert score > 0  # Signal haussier
    
    def test_predict_stock_overbought(self):
        """RSI surachat donne signal baissier."""
        service = PredictionService()
        
        stock_data = {
            'current_price': 100.0,
            'indicators': {
                'RSI': 85,  # Très surachat
                'MA_5': 102.0,
                'MA_20': 105.0,
                'volatility_daily': 0.02
            }
        }
        
        score = service.predict_stock(stock_data)
        
        assert score < 0  # Signal baissier
    
    def test_predict_stock_bullish_ma(self):
        """Prix au-dessus des MA = haussier."""
        service = PredictionService()
        
        stock_data = {
            'current_price': 110.0,
            'indicators': {
                'RSI': 55,
                'MA_5': 105.0,
                'MA_20': 100.0,  # Prix > MA5 > MA20
                'volatility_daily': 0.02
            }
        }
        
        score = service.predict_stock(stock_data)
        
        assert score > 0  # Tendance haussière
    
    def test_predict_stock_bearish_ma(self):
        """Prix en-dessous des MA = baissier."""
        service = PredictionService()
        
        stock_data = {
            'current_price': 90.0,
            'indicators': {
                'RSI': 45,
                'MA_5': 95.0,
                'MA_20': 100.0,  # Prix < MA5 < MA20
                'volatility_daily': 0.02
            }
        }
        
        score = service.predict_stock(stock_data)
        
        assert score < 0  # Tendance baissière
    
    def test_predict_stock_high_volatility(self):
        """Haute volatilité réduit le score."""
        service = PredictionService()
        
        # Même données sauf volatilité
        base_data = {
            'current_price': 110.0,
            'indicators': {
                'RSI': 55,
                'MA_5': 105.0,
                'MA_20': 100.0,
            }
        }
        
        low_vol_data = {**base_data, 'indicators': {**base_data['indicators'], 'volatility_daily': 0.01}}
        high_vol_data = {**base_data, 'indicators': {**base_data['indicators'], 'volatility_daily': 0.05}}
        
        low_vol_score = service.predict_stock(low_vol_data)
        high_vol_score = service.predict_stock(high_vol_data)
        
        # Score devrait être réduit avec haute volatilité
        assert abs(high_vol_score) <= abs(low_vol_score)
    
    def test_predict_stock_bounded(self):
        """Score toujours entre -1 et 1."""
        service = PredictionService()
        
        # Cas extrême haussier
        bullish = {
            'current_price': 150.0,
            'price_change_pct': 10.0,
            'indicators': {
                'RSI': 20,
                'MA_5': 140.0,
                'MA_20': 130.0,
                'volatility_daily': 0.005
            }
        }
        
        score = service.predict_stock(bullish)
        assert -1 <= score <= 1
    
    def test_predict_stock_missing_indicators(self):
        """Gère les indicateurs manquants."""
        service = PredictionService()
        
        stock_data = {
            'current_price': 100.0,
            'indicators': {}
        }
        
        score = service.predict_stock(stock_data)
        
        assert -1 <= score <= 1
    
    def test_predict_stock_no_indicators_key(self):
        """Gère l'absence de la clé indicators."""
        service = PredictionService()
        
        stock_data = {'current_price': 100.0}
        
        score = service.predict_stock(stock_data)
        
        assert -1 <= score <= 1


class TestPredictionServiceFeatureExtraction:
    """Tests pour l'extraction de features."""
    
    def test_extract_sports_features_complete(self):
        """Extraction complète des features sports."""
        service = PredictionService()
        
        match_data = {
            'home_team': {'win_rate': 0.6, 'goals_scored_avg': 2.0},
            'away_team': {'win_rate': 0.4, 'goals_scored_avg': 1.2},
            'odds': {'home_win': 1.8, 'draw': 3.5, 'away_win': 4.0}
        }
        
        features = service._extract_sports_features(match_data)
        
        assert isinstance(features, list)
        assert len(features) == 7
        assert all(isinstance(f, float) for f in features)
    
    def test_extract_sports_features_defaults(self):
        """Features par défaut pour données manquantes."""
        service = PredictionService()
        
        match_data = {}
        
        features = service._extract_sports_features(match_data)
        
        assert len(features) == 7
        # Valeurs par défaut utilisées
    
    def test_extract_finance_features_complete(self):
        """Extraction complète des features finance."""
        service = PredictionService()
        
        stock_data = {
            'price_change_pct': 1.5,
            'indicators': {
                'RSI': 55,
                'MA_5': 100.0,
                'MA_20': 98.0,
                'volatility_daily': 0.02
            }
        }
        
        features = service._extract_finance_features(stock_data)
        
        assert isinstance(features, list)
        assert len(features) == 5
        assert all(isinstance(f, float) for f in features)
    
    def test_extract_finance_features_defaults(self):
        """Features par défaut pour données manquantes."""
        service = PredictionService()
        
        stock_data = {}
        
        features = service._extract_finance_features(stock_data)
        
        assert len(features) == 5


class TestPredictionServiceHeuristics:
    """Tests pour les méthodes heuristiques."""
    
    def test_heuristic_sports_win_rate_impact(self):
        """Le win_rate impacte la prédiction."""
        service = PredictionService()
        
        # Domicile fort
        strong_home = {
            'home_team': {'win_rate': 0.8},
            'away_team': {'win_rate': 0.2},
        }
        
        # Domicile faible
        weak_home = {
            'home_team': {'win_rate': 0.2},
            'away_team': {'win_rate': 0.8},
        }
        
        score_strong = service._heuristic_sports_prediction(strong_home)
        score_weak = service._heuristic_sports_prediction(weak_home)
        
        assert score_strong > score_weak
    
    def test_heuristic_sports_odds_impact(self):
        """Les cotes impactent la prédiction."""
        service = PredictionService()
        
        # Domicile favori par cotes
        home_fav = {
            'odds': {'home_win': 1.5, 'away_win': 5.0}
        }
        
        # Extérieur favori par cotes
        away_fav = {
            'odds': {'home_win': 5.0, 'away_win': 1.5}
        }
        
        score_home_fav = service._heuristic_sports_prediction(home_fav)
        score_away_fav = service._heuristic_sports_prediction(away_fav)
        
        assert score_home_fav > score_away_fav
    
    def test_heuristic_finance_rsi_impact(self):
        """Le RSI impacte la prédiction."""
        service = PredictionService()
        
        oversold = {'indicators': {'RSI': 25}}
        overbought = {'indicators': {'RSI': 75}}
        
        score_oversold = service._heuristic_finance_prediction(oversold)
        score_overbought = service._heuristic_finance_prediction(overbought)
        
        assert score_oversold > score_overbought


class TestPredictionServiceMLModels:
    """Tests pour les modèles ML."""
    
    @patch('app.services.prediction_service.JOBLIB_AVAILABLE', False)
    def test_load_models_without_joblib(self):
        """Ne charge pas les modèles sans joblib."""
        service = PredictionService()
        service._load_models()
        
        assert service.sports_model is None
        assert service.finance_model is None
    
    @patch('app.services.prediction_service.JOBLIB_AVAILABLE', True)
    @patch('os.path.exists')
    def test_load_models_files_not_exist(self, mock_exists):
        """Ne charge pas si les fichiers n'existent pas."""
        mock_exists.return_value = False
        
        service = PredictionService()
        
        assert service.sports_model is None
        assert service.finance_model is None
    
    def test_predict_sport_with_ml_model(self):
        """Utilise le modèle ML pour les prédictions sportives."""
        service = PredictionService()
        
        # Mock du modèle
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = [[0.7, 0.2, 0.1]]
        service.sports_model = mock_model
        
        result = service.predict_sport({
            'home_team': {'win_rate': 0.5},
            'away_team': {'win_rate': 0.5}
        })
        
        assert result == 0.7
        mock_model.predict_proba.assert_called_once()
    
    def test_predict_sport_ml_exception_fallback(self):
        """Fallback vers heuristique si ML échoue."""
        service = PredictionService()
        
        # Mock qui lève une exception
        mock_model = MagicMock()
        mock_model.predict_proba.side_effect = Exception("ML error")
        service.sports_model = mock_model
        
        result = service.predict_sport({})
        
        # Doit retourner une valeur heuristique
        assert isinstance(result, float)
        assert 0 <= result <= 1
    
    def test_predict_stock_with_ml_model(self):
        """Utilise le modèle ML pour les prédictions finance."""
        service = PredictionService()
        
        # Mock du modèle
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.65]
        service.finance_model = mock_model
        
        result = service.predict_stock({'indicators': {}})
        
        assert result == 0.65
        mock_model.predict.assert_called_once()
    
    def test_predict_stock_with_scaler(self):
        """Utilise le scaler pour les prédictions finance."""
        service = PredictionService()
        
        # Mock du modèle et scaler
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.5]
        mock_scaler = MagicMock()
        mock_scaler.transform.return_value = [[1, 2, 3, 4, 5]]
        
        service.finance_model = mock_model
        service.finance_scaler = mock_scaler
        
        result = service.predict_stock({'indicators': {}})
        
        mock_scaler.transform.assert_called_once()
        assert result == 0.5
    
    def test_predict_stock_ml_exception_fallback(self):
        """Fallback vers heuristique si ML échoue."""
        service = PredictionService()
        
        # Mock qui lève une exception
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception("ML error")
        service.finance_model = mock_model
        
        result = service.predict_stock({})
        
        assert isinstance(result, float)
    
    def test_predict_sport_ml_empty_proba(self):
        """Gère predict_proba retournant tableau vide."""
        service = PredictionService()
        
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = [[]]
        service.sports_model = mock_model
        
        result = service.predict_sport({})
        
        assert result == 0.5  # Valeur par défaut


class TestPredictionServiceEdgeCases:
    """Tests des cas limites."""
    
    def test_heuristic_sports_non_numeric_values(self):
        """Gère les valeurs non numériques."""
        service = PredictionService()
        
        match_data = {
            'home_team': {'win_rate': 'high', 'goals_scored_avg': 'many'},
            'away_team': {'win_rate': None, 'goals_scored_avg': []},
            'odds': {'home_win': {}, 'away_win': []}
        }
        
        result = service._heuristic_sports_prediction(match_data)
        
        assert isinstance(result, float)
    
    def test_heuristic_finance_non_numeric_values(self):
        """Gère les valeurs non numériques en finance."""
        service = PredictionService()
        
        stock_data = {
            'current_price': 'expensive',
            'price_change_pct': {},
            'indicators': {
                'RSI': [],
                'MA_5': 'moving',
                'MA_20': None,
                'volatility_daily': {}
            }
        }
        
        result = service._heuristic_finance_prediction(stock_data)
        
        assert isinstance(result, float)
        assert -1 <= result <= 1
    
    def test_extract_sports_features_safe_float(self):
        """_extract_sports_features utilise safe_float."""
        service = PredictionService()
        
        features = service._extract_sports_features({
            'home_team': {'win_rate': None, 'goals_scored_avg': 'invalid'},
            'away_team': {},
            'odds': {}
        })
        
        # Devrait retourner des valeurs par défaut
        assert all(isinstance(f, float) for f in features)
        assert len(features) == 7
    
    def test_extract_finance_features_safe_float(self):
        """_extract_finance_features utilise safe_float."""
        service = PredictionService()
        
        features = service._extract_finance_features({
            'price_change_pct': 'up',
            'indicators': {
                'RSI': None,
                'MA_5': 'invalid'
            }
        })
        
        # Devrait retourner des valeurs par défaut (int ou float)
        assert all(isinstance(f, (int, float)) for f in features)
        assert len(features) == 5
