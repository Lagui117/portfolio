"""
Sports API Service for PredictWise.

This service handles fetching sports data from external APIs.
Currently using API-FOOTBALL (RapidAPI) as the primary provider.

Alternative APIs you can use:
- API-FOOTBALL: https://rapidapi.com/api-sports/api/api-football
- The Odds API: https://the-odds-api.com/
- SportMonks: https://www.sportmonks.com/
"""
import os
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SportsAPIService:
    """Service for fetching sports match data from external APIs."""
    
    def __init__(self):
        """Initialize the sports API service."""
        self.api_key = os.getenv('SPORTS_API_KEY', '')
        self.api_host = os.getenv('SPORTS_API_HOST', 'api-football-v1.p.rapidapi.com')
        self.use_mock = not self.api_key or os.getenv('USE_MOCK_SPORTS_API', 'false').lower() == 'true'
        
        if self.use_mock:
            logger.warning("Sports API running in MOCK mode. Set SPORTS_API_KEY to use real data.")
        else:
            logger.info(f"Sports API service initialized with host: {self.api_host}")
    
    def get_match_data(self, match_id: str) -> Dict[str, Any]:
        """
        Get detailed match information.
        
        Args:
            match_id: The unique identifier of the match
        
        Returns:
            Dictionary containing match data
        
        Raises:
            ValueError: If match_id is invalid or match not found
        """
        if self.use_mock:
            return self._get_mock_match_data(match_id)
        
        try:
            # Appel à l'API réelle (exemple avec API-FOOTBALL)
            url = f"https://{self.api_host}/v3/fixtures"
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": self.api_host
            }
            params = {"id": match_id}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('response'):
                logger.warning(f"No match found for ID: {match_id}")
                return self._get_mock_match_data(match_id)
            
            fixture = data['response'][0]
            return self._format_match_data(fixture)
            
        except Exception as e:
            logger.error(f"Error fetching match data: {e}")
            logger.info("Falling back to mock data")
            return self._get_mock_match_data(match_id)
    
    def _format_match_data(self, fixture: Dict) -> Dict[str, Any]:
        """Format API response into standardized match data."""
        return {
            'match_id': str(fixture['fixture']['id']),
            'sport': 'football',
            'league': fixture['league']['name'],
            'country': fixture['league']['country'],
            'date': fixture['fixture']['date'],
            'venue': fixture['fixture']['venue']['name'],
            'status': fixture['fixture']['status']['short'],
            'home_team': {
                'id': fixture['teams']['home']['id'],
                'name': fixture['teams']['home']['name'],
                'logo': fixture['teams']['home']['logo']
            },
            'away_team': {
                'id': fixture['teams']['away']['id'],
                'name': fixture['teams']['away']['name'],
                'logo': fixture['teams']['away']['logo']
            },
            'odds': fixture.get('odds', {}),
            'score': {
                'home': fixture['goals'].get('home'),
                'away': fixture['goals'].get('away')
            } if fixture.get('goals') else None
        }
    
    def _get_mock_match_data(self, match_id: str) -> Dict[str, Any]:
        """
        Generate mock match data for testing/demo purposes.
        
        PRODUCTION: Replace this with actual API calls to:
        - API-FOOTBALL (RapidAPI): https://rapidapi.com/api-sports/api/api-football
        - The Odds API: https://the-odds-api.com/
        """
        mock_matches = {
            '1': {
                'match_id': '1',
                'sport': 'football',
                'league': 'Premier League',
                'country': 'England',
                'date': (datetime.now() + timedelta(days=2)).isoformat(),
                'venue': 'Old Trafford',
                'status': 'NS',  # Not Started
                'home_team': {
                    'id': '33',
                    'name': 'Manchester United',
                    'logo': 'https://media.api-sports.io/football/teams/33.png',
                    'recent_form': 'WWDWL',
                    'goals_scored_avg': 1.8,
                    'goals_conceded_avg': 1.2,
                    'win_rate': 0.65
                },
                'away_team': {
                    'id': '40',
                    'name': 'Liverpool',
                    'logo': 'https://media.api-sports.io/football/teams/40.png',
                    'recent_form': 'WWWDW',
                    'goals_scored_avg': 2.3,
                    'goals_conceded_avg': 0.9,
                    'win_rate': 0.75
                },
                'odds': {
                    'home_win': 2.80,
                    'draw': 3.40,
                    'away_win': 2.50
                },
                'h2h_stats': {
                    'last_5_matches': 'ALHDA',  # A=Away win, L=Home Loss, H=Home win, D=Draw
                    'home_wins': 2,
                    'draws': 1,
                    'away_wins': 2
                }
            },
            '2': {
                'match_id': '2',
                'sport': 'football',
                'league': 'La Liga',
                'country': 'Spain',
                'date': (datetime.now() + timedelta(days=1)).isoformat(),
                'venue': 'Camp Nou',
                'status': 'NS',
                'home_team': {
                    'id': '529',
                    'name': 'Barcelona',
                    'logo': 'https://media.api-sports.io/football/teams/529.png',
                    'recent_form': 'WWWWW',
                    'goals_scored_avg': 2.8,
                    'goals_conceded_avg': 0.6,
                    'win_rate': 0.85
                },
                'away_team': {
                    'id': '541',
                    'name': 'Real Madrid',
                    'logo': 'https://media.api-sports.io/football/teams/541.png',
                    'recent_form': 'WWDWW',
                    'goals_scored_avg': 2.5,
                    'goals_conceded_avg': 0.8,
                    'win_rate': 0.78
                },
                'odds': {
                    'home_win': 2.20,
                    'draw': 3.60,
                    'away_win': 3.00
                },
                'h2h_stats': {
                    'last_5_matches': 'HDDHH',
                    'home_wins': 3,
                    'draws': 2,
                    'away_wins': 0
                }
            }
        }
        
        if match_id not in mock_matches:
            # Générer des données aléatoires pour les IDs inconnus
            return self._generate_random_match(match_id)
        
        return mock_matches[match_id]
    
    def _generate_random_match(self, match_id: str) -> Dict[str, Any]:
        """Generate random match data for unknown match IDs."""
        import random
        
        teams = [
            'Arsenal', 'Chelsea', 'Bayern Munich', 'Juventus', 'PSG',
            'Inter Milan', 'Atletico Madrid', 'Borussia Dortmund'
        ]
        
        home_team = random.choice(teams)
        away_team = random.choice([t for t in teams if t != home_team])
        
        return {
            'match_id': match_id,
            'sport': 'football',
            'league': 'International Friendly',
            'country': 'International',
            'date': (datetime.now() + timedelta(days=random.randint(1, 7))).isoformat(),
            'venue': f'{home_team} Stadium',
            'status': 'NS',
            'home_team': {
                'id': match_id + '00',
                'name': home_team,
                'recent_form': ''.join(random.choices(['W', 'D', 'L'], k=5)),
                'goals_scored_avg': round(random.uniform(1.0, 3.0), 1),
                'goals_conceded_avg': round(random.uniform(0.5, 2.0), 1),
                'win_rate': round(random.uniform(0.4, 0.8), 2)
            },
            'away_team': {
                'id': match_id + '01',
                'name': away_team,
                'recent_form': ''.join(random.choices(['W', 'D', 'L'], k=5)),
                'goals_scored_avg': round(random.uniform(1.0, 3.0), 1),
                'goals_conceded_avg': round(random.uniform(0.5, 2.0), 1),
                'win_rate': round(random.uniform(0.4, 0.8), 2)
            },
            'odds': {
                'home_win': round(random.uniform(1.5, 4.0), 2),
                'draw': round(random.uniform(3.0, 4.0), 2),
                'away_win': round(random.uniform(1.5, 4.0), 2)
            }
        }
    
    def get_upcoming_matches(self, league_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of upcoming matches.
        
        Args:
            league_id: Optional league identifier to filter matches
            limit: Maximum number of matches to return
        
        Returns:
            List of match dictionaries
        """
        if self.use_mock:
            return [self._get_mock_match_data(str(i)) for i in range(1, min(limit + 1, 6))]
        
        # TODO: Implémenter avec vraie API
        return [self._get_mock_match_data(str(i)) for i in range(1, min(limit + 1, 6))]


# Instance globale du service
sports_api_service = SportsAPIService()
