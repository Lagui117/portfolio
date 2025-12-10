"""Sports data service with ML prediction capabilities."""
import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import joblib
import numpy as np
from app.models.sport_event import SportEvent, TeamStatistics
from app.core.database import db


class SportsService:
    """Service for fetching sports data and making ML predictions."""
    
    def __init__(self):
        self.api_key = os.getenv('SPORTS_API_KEY', '')
        self.base_url = os.getenv('SPORTS_API_URL', 'https://api-sports.io/v1')
        self.model = None
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load the trained ML model for sports predictions."""
        model_path = os.path.join(
            os.path.dirname(__file__),
            '../../ml/models/sports_model.pkl'
        )
        try:
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                self.model_loaded = True
                print(f"✅ Sports ML model loaded from {model_path}")
            else:
                print(f"⚠️  Sports model not found at {model_path}. Using fallback predictions.")
        except Exception as e:
            print(f"⚠️  Failed to load sports model: {e}")
            self.model_loaded = False
    
    def get_upcoming_matches(
        self, 
        sport: str = 'football', 
        league: str = None,
        days_ahead: int = 7,
        limit: int = 20
    ) -> List[Dict]:
        """
        Fetch upcoming matches from database or external API.
        
        Args:
            sport: Sport type (football, basketball, etc.)
            league: League name filter
            days_ahead: Number of days to look ahead
            limit: Maximum number of results
            
        Returns:
            List of match dictionaries
        """
        # Try to get from database first
        query = SportEvent.query.filter_by(sport_type=sport, status='scheduled')
        
        if league:
            query = query.filter_by(league=league)
        
        end_date = datetime.utcnow() + timedelta(days=days_ahead)
        query = query.filter(
            SportEvent.event_date >= datetime.utcnow(),
            SportEvent.event_date <= end_date
        )
        
        events = query.order_by(SportEvent.event_date).limit(limit).all()
        
        if events:
            return [event.to_dict() for event in events]
        
        # If no data in DB, use mock or API
        return self._get_mock_matches(sport, league, limit)
    
    def get_match_by_id(self, event_id: int) -> Optional[Dict]:
        """
        Get a specific match by ID.
        
        Args:
            event_id: Event ID
            
        Returns:
            Match dictionary or None
        """
        event = SportEvent.query.get(event_id)
        return event.to_dict() if event else None
    
    def get_team_statistics(
        self, 
        team_name: str, 
        sport: str = 'football',
        season: str = None
    ) -> Dict:
        """
        Fetch team statistics.
        
        Args:
            team_name: Team name
            sport: Sport type
            season: Season (e.g., "2024-2025")
            
        Returns:
            Statistics dictionary
        """
        if season is None:
            season = self._get_current_season()
        
        stats = TeamStatistics.query.filter_by(
            team_name=team_name,
            sport_type=sport,
            season=season
        ).first()
        
        if stats:
            return stats.to_dict()
        
        # Return mock data if not in database
        return self._get_mock_team_stats(team_name, sport)
    
    def predict_match_outcome(
        self, 
        home_team: str, 
        away_team: str, 
        sport: str,
        league: str = None,
        additional_features: Dict = None
    ) -> Dict:
        """
        Predict match outcome using ML model.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            sport: Sport type
            league: League name
            additional_features: Additional features for prediction
            
        Returns:
            Prediction dictionary with result and probabilities
        """
        # Get team statistics
        home_stats = self.get_team_statistics(home_team, sport)
        away_stats = self.get_team_statistics(away_team, sport)
        
        # Prepare features
        features = self._prepare_prediction_features(
            home_stats, 
            away_stats, 
            additional_features or {}
        )
        
        if self.model_loaded and self.model is not None:
            try:
                # Make prediction with real model
                X = np.array([list(features.values())])
                prediction = self.model.predict(X)[0]
                probabilities = self.model.predict_proba(X)[0]
                
                result_map = {0: 'AWAY_WIN', 1: 'DRAW', 2: 'HOME_WIN'}
                result = result_map[prediction]
                
                return {
                    'result': result,
                    'confidence': float(max(probabilities)),
                    'probabilities': {
                        'home_win': float(probabilities[2]),
                        'draw': float(probabilities[1]),
                        'away_win': float(probabilities[0])
                    },
                    'model_version': 'v1.0',
                    'features_used': list(features.keys())
                }
            except Exception as e:
                print(f"Error during prediction: {e}")
                return self._fallback_prediction(home_stats, away_stats)
        else:
            # Fallback prediction based on statistics
            return self._fallback_prediction(home_stats, away_stats)
    
    def _prepare_prediction_features(
        self, 
        home_stats: Dict, 
        away_stats: Dict,
        additional: Dict
    ) -> Dict:
        """Prepare features for ML model."""
        return {
            'home_wins': home_stats.get('wins', 0),
            'home_losses': home_stats.get('losses', 0),
            'away_wins': away_stats.get('wins', 0),
            'away_losses': away_stats.get('losses', 0),
            'home_goals_avg': home_stats.get('avg_goals_scored', 0),
            'away_goals_avg': away_stats.get('avg_goals_scored', 0),
        }
    
    def _fallback_prediction(self, home_stats: Dict, away_stats: Dict) -> Dict:
        """Simple rule-based prediction when ML model is not available."""
        home_win_rate = home_stats.get('win_rate', 0)
        away_win_rate = away_stats.get('win_rate', 0)
        
        # Simple heuristic
        if home_win_rate > away_win_rate + 0.15:
            result = 'HOME_WIN'
            conf = 0.65
        elif away_win_rate > home_win_rate + 0.15:
            result = 'AWAY_WIN'
            conf = 0.62
        else:
            result = 'DRAW'
            conf = 0.55
        
        return {
            'result': result,
            'confidence': conf,
            'probabilities': {
                'home_win': 0.45 if result == 'HOME_WIN' else 0.25,
                'draw': 0.35 if result == 'DRAW' else 0.25,
                'away_win': 0.45 if result == 'AWAY_WIN' else 0.30
            },
            'model_version': 'fallback',
            'note': 'Prédiction basée sur les statistiques (modèle ML non disponible)'
        }
    
    def _get_current_season(self) -> str:
        """Get current season string."""
        now = datetime.now()
        if now.month >= 8:
            return f"{now.year}-{now.year + 1}"
        else:
            return f"{now.year - 1}-{now.year}"
    
    def _get_mock_matches(self, sport: str, league: str, limit: int) -> List[Dict]:
        """Generate mock match data for development."""
        matches = []
        teams = [
            ('Manchester United', 'Liverpool'),
            ('Barcelona', 'Real Madrid'),
            ('Bayern Munich', 'Borussia Dortmund'),
            ('PSG', 'Olympique Marseille'),
            ('Juventus', 'Inter Milan'),
        ]
        
        for i, (home, away) in enumerate(teams[:limit]):
            match_date = datetime.utcnow() + timedelta(days=i+1, hours=i*3)
            matches.append({
                'id': i + 1,
                'sport_type': sport,
                'league': league or 'Premier League',
                'home_team': home,
                'away_team': away,
                'event_date': match_date.isoformat(),
                'status': 'scheduled',
                'odds': {
                    'home': round(1.5 + i * 0.1, 2),
                    'draw': round(3.2 + i * 0.1, 2),
                    'away': round(4.0 + i * 0.2, 2)
                }
            })
        
        return matches
    
    def _get_mock_team_stats(self, team_name: str, sport: str) -> Dict:
        """Return mock team statistics."""
        import random
        random.seed(hash(team_name))
        
        matches_played = random.randint(25, 38)
        wins = random.randint(10, 25)
        draws = random.randint(5, 12)
        losses = matches_played - wins - draws
        
        return {
            'team_name': team_name,
            'sport_type': sport,
            'matches_played': matches_played,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_for': random.randint(40, 85),
            'goals_against': random.randint(25, 60),
            'win_rate': round(wins / matches_played, 3),
            'avg_goals_scored': round(random.uniform(1.2, 2.5), 2),
            'avg_goals_conceded': round(random.uniform(0.8, 1.8), 2),
            'recent_form': 'WWDLW'
        }
