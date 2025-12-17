"""
Service de prediction ML.
Calcule les scores de prediction pour sports et finance.

NOTE: Ce service utilise des modeles simplifies ou mock.
Pour un projet reel, entrainer et charger de vrais modeles ML.
"""

import os
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Essayer de charger joblib pour les modeles
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    logger.warning("joblib non disponible. Service prediction en mode mock.")
    JOBLIB_AVAILABLE = False


class PredictionService:
    """Service centralise pour les predictions ML."""
    
    def __init__(self):
        """Initialise le service de prediction."""
        self.sports_model = None
        self.finance_model = None
        self.finance_scaler = None
        
        # Chemins des modeles
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.ml_models_dir = os.path.join(base_dir, '..', 'ml', 'models')
        
        # Charger les modeles si disponibles
        self._load_models()
    
    def _load_models(self):
        """Charge les modeles ML depuis le disque."""
        if not JOBLIB_AVAILABLE:
            logger.info("Modeles ML non charges (joblib indisponible)")
            return
        
        # Modele sports
        sports_path = os.path.join(self.ml_models_dir, 'sports_model.pkl')
        if os.path.exists(sports_path):
            try:
                self.sports_model = joblib.load(sports_path)
                logger.info(f"Modele sports charge: {sports_path}")
            except Exception as e:
                logger.warning(f"Erreur chargement modele sports: {e}")
        
        # Modele finance
        finance_path = os.path.join(self.ml_models_dir, 'finance_model.pkl')
        if os.path.exists(finance_path):
            try:
                self.finance_model = joblib.load(finance_path)
                logger.info(f"Modele finance charge: {finance_path}")
            except Exception as e:
                logger.warning(f"Erreur chargement modele finance: {e}")
        
        # Scaler finance
        scaler_path = os.path.join(self.ml_models_dir, 'finance_scaler.pkl')
        if os.path.exists(scaler_path):
            try:
                self.finance_scaler = joblib.load(scaler_path)
                logger.info(f"Scaler finance charge: {scaler_path}")
            except Exception as e:
                logger.warning(f"Erreur chargement scaler finance: {e}")

    def predict_sport(self, match_data: Dict[str, Any]) -> float:
        """
        Predit le resultat d'un match sportif.
        
        Args:
            match_data: Donnees du match (equipes, stats, cotes, etc.)
        
        Returns:
            Score de probabilite entre 0 et 1 (victoire equipe domicile).
        """
        # Si modele ML disponible, l'utiliser
        if self.sports_model is not None:
            try:
                features = self._extract_sports_features(match_data)
                proba = self.sports_model.predict_proba([features])[0]
                # Retourner la probabilite de victoire domicile
                return float(proba[0]) if len(proba) > 0 else 0.5
            except Exception as e:
                logger.warning(f"Erreur prediction ML sports: {e}")
        
        # Sinon, utiliser une heuristique simple
        return self._heuristic_sports_prediction(match_data)
    
    def _extract_sports_features(self, match_data: Dict[str, Any]) -> List[float]:
        """Extrait les features pour le modele ML sports."""
        home = match_data.get('home_team', {})
        away = match_data.get('away_team', {})
        odds = match_data.get('odds', {})
        
        def safe_float(val, default=0.5):
            try:
                return float(val) if val is not None else default
            except (ValueError, TypeError):
                return default
        
        features = [
            safe_float(home.get('win_rate'), 0.5),
            safe_float(home.get('goals_scored_avg'), 1.5),
            safe_float(away.get('win_rate'), 0.5),
            safe_float(away.get('goals_scored_avg'), 1.5),
            safe_float(odds.get('home_win'), 2.5),
            safe_float(odds.get('draw'), 3.2),
            safe_float(odds.get('away_win'), 2.5),
        ]
        
        return features
    
    def _heuristic_sports_prediction(self, match_data: Dict[str, Any]) -> float:
        """
        Prediction heuristique simple basee sur les cotes et stats.
        
        Cette methode est utilisee quand aucun modele ML n'est disponible.
        Elle combine plusieurs facteurs avec des poids simples.
        """
        home = match_data.get('home_team', {})
        away = match_data.get('away_team', {})
        odds = match_data.get('odds', {})
        
        score = 0.5  # Score de base (50/50)
        
        # Ajustement selon les taux de victoire
        home_wr = home.get('win_rate', 0.5)
        away_wr = away.get('win_rate', 0.5)
        if isinstance(home_wr, (int, float)) and isinstance(away_wr, (int, float)):
            diff = (home_wr - away_wr) * 0.3
            score += diff
        
        # Ajustement selon les cotes (si disponibles)
        home_odds = odds.get('home_win')
        away_odds = odds.get('away_win')
        if home_odds and away_odds:
            try:
                home_odds = float(home_odds)
                away_odds = float(away_odds)
                # Cotes plus basses = favori
                odds_factor = (away_odds - home_odds) / (home_odds + away_odds) * 0.2
                score += odds_factor
            except (ValueError, TypeError, ZeroDivisionError):
                pass
        
        # Ajustement selon les buts moyens
        home_goals = home.get('goals_scored_avg', 1.5)
        away_goals = away.get('goals_scored_avg', 1.5)
        if isinstance(home_goals, (int, float)) and isinstance(away_goals, (int, float)):
            goals_factor = (home_goals - away_goals) * 0.1
            score += goals_factor
        
        # Borner le score entre 0.1 et 0.9
        score = max(0.1, min(0.9, score))
        
        return round(score, 3)

    def predict_stock(self, stock_data: Dict[str, Any]) -> float:
        """
        Predit la tendance d'un actif financier.
        
        Args:
            stock_data: Donnees de l'actif (prix, indicateurs, etc.)
        
        Returns:
            Score entre -1 (forte baisse) et 1 (forte hausse), ou 0 (neutre).
        """
        # Si modele ML disponible, l'utiliser
        if self.finance_model is not None:
            try:
                features = self._extract_finance_features(stock_data)
                if self.finance_scaler:
                    features = self.finance_scaler.transform([features])[0]
                prediction = self.finance_model.predict([features])[0]
                return float(prediction)
            except Exception as e:
                logger.warning(f"Erreur prediction ML finance: {e}")
        
        # Sinon, utiliser une heuristique simple
        return self._heuristic_finance_prediction(stock_data)
    
    def _extract_finance_features(self, stock_data: Dict[str, Any]) -> List[float]:
        """Extrait les features pour le modele ML finance."""
        indicators = stock_data.get('indicators', {})
        
        def safe_float(val, default=0.0):
            try:
                return float(val) if val is not None else default
            except (ValueError, TypeError):
                return default
        
        features = [
            safe_float(indicators.get('RSI'), 50),
            safe_float(indicators.get('MA_5'), 0),
            safe_float(indicators.get('MA_20'), 0),
            safe_float(indicators.get('volatility_daily'), 0.02),
            safe_float(stock_data.get('price_change_pct'), 0),
        ]
        
        return features
    
    def _heuristic_finance_prediction(self, stock_data: Dict[str, Any]) -> float:
        """
        Prediction heuristique simple basee sur les indicateurs techniques.
        
        Retourne un score entre -1 (baisse) et 1 (hausse).
        """
        indicators = stock_data.get('indicators', {})
        score = 0.0
        
        # RSI (Relative Strength Index)
        rsi = indicators.get('RSI')
        if rsi is not None:
            try:
                rsi = float(rsi)
                if rsi < 30:  # Survendu -> potentiel hausse
                    score += 0.3
                elif rsi > 70:  # Surachete -> potentiel baisse
                    score -= 0.3
            except (ValueError, TypeError):
                pass
        
        # Moyennes mobiles (MA)
        ma_5 = indicators.get('MA_5')
        ma_20 = indicators.get('MA_20')
        current = stock_data.get('current_price')
        
        if ma_5 and ma_20 and current:
            try:
                ma_5 = float(ma_5)
                ma_20 = float(ma_20)
                current = float(current)
                
                # Prix au-dessus de MA -> tendance haussiere
                if current > ma_5 > ma_20:
                    score += 0.4
                elif current < ma_5 < ma_20:
                    score -= 0.4
            except (ValueError, TypeError):
                pass
        
        # Volatilite
        volatility = indicators.get('volatility_daily')
        if volatility is not None:
            try:
                volatility = float(volatility)
                # Haute volatilite -> incertitude
                if volatility > 0.03:
                    score *= 0.8  # Reduire la confiance
            except (ValueError, TypeError):
                pass
        
        # Variation recente
        change = stock_data.get('price_change_pct')
        if change is not None:
            try:
                change = float(change)
                score += change * 0.02  # Leger impact
            except (ValueError, TypeError):
                pass
        
        # Borner le score entre -1 et 1
        score = max(-1.0, min(1.0, score))
        
        return round(score, 3)


# Instance globale du service
prediction_service = PredictionService()
