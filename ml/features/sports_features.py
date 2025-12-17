"""
Sports Feature Engineering
Extracts features for sports match prediction.
"""

import numpy as np
from typing import Dict, List, Any
import sys
import os

# Add parent directory to path for imports
ml_dir = os.path.dirname(os.path.dirname(__file__))
if ml_dir not in sys.path:
    sys.path.insert(0, ml_dir)

from utils.exceptions import MissingFeatureError


class SportsFeatureExtractor:
    """
    Extracts features from sports match data for ML prediction.
    
    Features extracted:
    - Form difference (recent results)
    - Goals scored/conceded ratio
    - Home/Away performance
    - Head-to-head history
    - Expected goals metrics
    - Team momentum
    - Fatigue indicator
    """
    
    REQUIRED_FEATURES = [
        'home_form',
        'away_form',
        'home_attack',
        'away_attack',
        'home_defense',
        'away_defense',
        'home_goals_scored',
        'away_goals_scored',
        'home_goals_conceded',
        'away_goals_conceded',
        'home_win_rate',
        'away_win_rate',
        'is_home'
    ]
    
    def __init__(self):
        self.feature_names = None
    
    def extract(self, match_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract features from match data.
        
        Args:
            match_data: Dictionary with match statistics
            
        Returns:
            Feature array ready for model input
        """
        # Validate required features
        missing_features = [
            feat for feat in self.REQUIRED_FEATURES
            if feat not in match_data
        ]
        
        if missing_features:
            raise MissingFeatureError(
                f"Missing required features: {missing_features}"
            )
        
        features = []
        
        # 1. Form difference (from recent results)
        home_form_data = match_data.get('home_form', [])
        away_form_data = match_data.get('away_form', [])
        
        # Calculate form score (2=Win, 1=Draw, 0=Loss)
        if isinstance(home_form_data, list) and len(home_form_data) > 0:
            home_form_score = sum(home_form_data) / len(home_form_data)
        else:
            home_form_score = 1.0
        
        if isinstance(away_form_data, list) and len(away_form_data) > 0:
            away_form_score = sum(away_form_data) / len(away_form_data)
        else:
            away_form_score = 1.0
        
        form_diff = home_form_score - away_form_score
        features.append(form_diff)
        
        # 2. Offensive power difference
        home_attack = match_data.get('home_attack', 70.0)
        away_attack = match_data.get('away_attack', 70.0)
        attack_diff = home_attack - away_attack
        features.append(attack_diff)
        
        # 3. Defensive power difference
        home_defense = match_data.get('home_defense', 70.0)
        away_defense = match_data.get('away_defense', 70.0)
        defense_diff = home_defense - away_defense
        features.append(defense_diff)
        
        # 4. Goal difference ratio
        home_goals_scored = match_data.get('home_goals_scored', 15)
        away_goals_scored = match_data.get('away_goals_scored', 15)
        home_goals_conceded = match_data.get('home_goals_conceded', 10)
        away_goals_conceded = match_data.get('away_goals_conceded', 10)
        
        home_gd = home_goals_scored - home_goals_conceded
        away_gd = away_goals_scored - away_goals_conceded
        gd_ratio = (home_gd - away_gd) / 10.0  # Normalize
        features.append(gd_ratio)
        
        # 5. Win rate difference
        home_wr = match_data.get('home_win_rate', 0.5)
        away_wr = match_data.get('away_win_rate', 0.5)
        wr_diff = home_wr - away_wr
        features.append(wr_diff)
        
        # 6. Home advantage factor
        home_advantage = 1.0 if match_data.get('is_home', True) else 0.0
        features.append(home_advantage)
        
        # 7. Expected goals (xG) difference
        home_xg_data = match_data.get('home_xg', [])
        away_xg_data = match_data.get('away_xg', [])
        
        # Calculate average xG from recent matches
        if isinstance(home_xg_data, list) and len(home_xg_data) > 0:
            home_xg_avg = sum(home_xg_data) / len(home_xg_data)
        else:
            home_xg_avg = home_attack / 100.0
        
        if isinstance(away_xg_data, list) and len(away_xg_data) > 0:
            away_xg_avg = sum(away_xg_data) / len(away_xg_data)
        else:
            away_xg_avg = away_attack / 100.0
        
        xg_diff = home_xg_avg - away_xg_avg
        features.append(xg_diff)
        
        # 8. Head-to-head history
        h2h_history = match_data.get('h2h_history', [])
        
        if isinstance(h2h_history, list) and len(h2h_history) > 0:
            # h2h_history contains results: 0=Home win, 1=Draw, 2=Away win
            h2h_home_wins = sum(1 for r in h2h_history if r == 0 or r == 1)
            h2h_total = len(h2h_history)
            h2h_home_rate = h2h_home_wins / h2h_total
        else:
            h2h_home_rate = 0.5
        
        features.append(h2h_home_rate)
        
        # 9. Momentum (recent trend)
        home_momentum = match_data.get('home_momentum', 0.5)
        away_momentum = match_data.get('away_momentum', 0.5)
        momentum_diff = home_momentum - away_momentum
        features.append(momentum_diff)
        
        # 10. Fatigue indicator
        home_days_rest = match_data.get('home_days_since_last_match', 7)
        away_days_rest = match_data.get('away_days_since_last_match', 7)
        fatigue_diff = (away_days_rest - home_days_rest) / 7.0  # Normalized
        features.append(fatigue_diff)
        
        # Store feature names for reference
        self.feature_names = [
            'form_diff',
            'attack_diff',
            'defense_diff',
            'goal_diff_ratio',
            'win_rate_diff',
            'home_advantage',
            'xg_diff',
            'h2h_home_rate',
            'momentum_diff',
            'fatigue_diff'
        ]
        
        return np.array(features).reshape(1, -1)
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names in order."""
        if self.feature_names is None:
            return [
                'form_diff',
                'attack_diff',
                'defense_diff',
                'goal_diff_ratio',
                'win_rate_diff',
                'home_advantage',
                'xg_diff',
                'h2h_home_rate',
                'momentum_diff',
                'fatigue_diff'
            ]
        return self.feature_names
    
    @staticmethod
    def create_sample_data(home_stronger: bool = True) -> Dict[str, Any]:
        """
        Create sample match data for testing.
        
        Args:
            home_stronger: If True, home team is statistically stronger
            
        Returns:
            Sample match data dictionary
        """
        if home_stronger:
            return {
                'home_form': [2, 1, 2, 2, 1],  # W, D, W, W, D
                'away_form': [0, 1, 0, 2, 1],  # L, D, L, W, D
                'home_attack': 82.5,
                'away_attack': 72.3,
                'home_defense': 79.8,
                'away_defense': 74.1,
                'home_goals_scored': 18,
                'away_goals_scored': 12,
                'home_goals_conceded': 8,
                'away_goals_conceded': 14,
                'home_win_rate': 0.68,
                'away_win_rate': 0.42,
                'is_home': True,
                'home_xg': [2.1, 1.8, 2.3, 2.0, 1.9],
                'away_xg': [1.2, 1.5, 1.1, 1.8, 1.4],
                'h2h_history': [1, 0, 1, 2, 0],  # D, Home, D, Away, Home
                'home_rest_days': 4,
                'away_rest_days': 3,
                'home_momentum': 0.72,
                'away_momentum': 0.48
            }
        else:
            return {
                'home_form': [1, 2, 0, 1, 2],  # D, W, L, D, W
                'away_form': [2, 1, 0, 1, 2],  # W, D, L, D, W
                'home_attack': 75.0,
                'away_attack': 75.0,
                'home_defense': 75.0,
                'away_defense': 75.0,
                'home_goals_scored': 15,
                'away_goals_scored': 15,
                'home_goals_conceded': 12,
                'away_goals_conceded': 12,
                'home_win_rate': 0.50,
                'away_win_rate': 0.50,
                'is_home': True,
                'home_xg': [1.5, 1.6, 1.4, 1.5, 1.6],
                'away_xg': [1.5, 1.4, 1.6, 1.5, 1.4],
                'h2h_history': [1, 1, 2, 0, 1],  # balanced
                'home_rest_days': 5,
                'away_rest_days': 5,
                'home_momentum': 0.50,
                'away_momentum': 0.50
            }
