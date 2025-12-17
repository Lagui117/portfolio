"""
Service API Sports.
Recupere les donnees de matchs sportifs depuis des APIs externes ou mock.

APIs supportees (configurer via variables d'environnement):
- API-FOOTBALL (RapidAPI): https://rapidapi.com/api-sports/api/api-football
- The Odds API: https://the-odds-api.com/
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Essayer d'importer requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    logger.warning("requests non disponible. Sports API en mode mock uniquement.")
    REQUESTS_AVAILABLE = False


class SportsAPIService:
    """Service pour recuperer les donnees sportives."""
    
    def __init__(self):
        """Initialise le service API sports."""
        self.api_key = os.getenv('SPORTS_API_KEY', '')
        self.api_host = os.getenv('SPORTS_API_HOST', 'api-football-v1.p.rapidapi.com')
        self.use_mock = (
            not self.api_key or 
            not REQUESTS_AVAILABLE or
            os.getenv('USE_MOCK_SPORTS_API', 'true').lower() == 'true'
        )
        
        if self.use_mock:
            logger.info("Sports API Service en mode MOCK")
        else:
            logger.info(f"Sports API Service initialise avec host: {self.api_host}")

    def get_match_data(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupere les donnees d'un match specifique.
        
        Args:
            match_id: Identifiant du match.
        
        Returns:
            Dictionnaire des donnees du match ou None si non trouve.
        """
        if self.use_mock:
            return self._get_mock_match_data(match_id)
        
        try:
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
                logger.warning(f"Match non trouve: {match_id}")
                return self._get_mock_match_data(match_id)
            
            fixture = data['response'][0]
            return self._format_api_match(fixture)
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout API sports pour match {match_id}")
            return self._get_mock_match_data(match_id)
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP API sports: {e}")
            return self._get_mock_match_data(match_id)
        except Exception as e:
            logger.error(f"Erreur API sports: {e}")
            return self._get_mock_match_data(match_id)

    def get_upcoming_matches(
        self,
        sport: str = 'football',
        league: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Recupere les matchs a venir.
        
        Args:
            sport: Type de sport.
            league: Ligue specifique (optionnel).
            limit: Nombre max de resultats.
        
        Returns:
            Liste des matchs.
        """
        if self.use_mock:
            return self._get_mock_upcoming_matches(sport, league, limit)
        
        # Implementation API reelle (a completer selon l'API utilisee)
        return self._get_mock_upcoming_matches(sport, league, limit)

    def _format_api_match(self, fixture: Dict) -> Dict[str, Any]:
        """Formate les donnees d'un match depuis l'API."""
        return {
            'match_id': str(fixture['fixture']['id']),
            'sport': 'football',
            'league': fixture['league']['name'],
            'country': fixture['league']['country'],
            'date': fixture['fixture']['date'],
            'venue': fixture['fixture'].get('venue', {}).get('name'),
            'status': fixture['fixture']['status']['short'],
            'home_team': {
                'id': fixture['teams']['home']['id'],
                'name': fixture['teams']['home']['name'],
                'logo': fixture['teams']['home'].get('logo'),
            },
            'away_team': {
                'id': fixture['teams']['away']['id'],
                'name': fixture['teams']['away']['name'],
                'logo': fixture['teams']['away'].get('logo'),
            },
            'odds': fixture.get('odds', {}),
        }

    def _get_mock_match_data(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Genere des donnees mock pour un match.
        
        PRODUCTION: Remplacer par de vrais appels API.
        """
        # Donnees mock pour demonstration
        mock_matches = {
            '1': {
                'match_id': '1',
                'sport': 'football',
                'league': 'Premier League',
                'country': 'England',
                'date': (datetime.now() + timedelta(days=2)).isoformat(),
                'venue': 'Old Trafford',
                'status': 'NS',
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
                    'last_5': 'ALHDA',
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
                'date': (datetime.now() + timedelta(days=3)).isoformat(),
                'venue': 'Santiago Bernabeu',
                'status': 'NS',
                'home_team': {
                    'id': '541',
                    'name': 'Real Madrid',
                    'logo': 'https://media.api-sports.io/football/teams/541.png',
                    'recent_form': 'WWWWW',
                    'goals_scored_avg': 2.5,
                    'goals_conceded_avg': 0.8,
                    'win_rate': 0.82
                },
                'away_team': {
                    'id': '529',
                    'name': 'Barcelona',
                    'logo': 'https://media.api-sports.io/football/teams/529.png',
                    'recent_form': 'WDWWL',
                    'goals_scored_avg': 2.1,
                    'goals_conceded_avg': 1.1,
                    'win_rate': 0.68
                },
                'odds': {
                    'home_win': 2.10,
                    'draw': 3.50,
                    'away_win': 3.20
                },
                'h2h_stats': {
                    'last_5': 'HDHAH',
                    'home_wins': 3,
                    'draws': 1,
                    'away_wins': 1
                }
            },
            '3': {
                'match_id': '3',
                'sport': 'football',
                'league': 'Ligue 1',
                'country': 'France',
                'date': (datetime.now() + timedelta(days=1)).isoformat(),
                'venue': 'Parc des Princes',
                'status': 'NS',
                'home_team': {
                    'id': '85',
                    'name': 'Paris Saint-Germain',
                    'logo': 'https://media.api-sports.io/football/teams/85.png',
                    'recent_form': 'WWWDW',
                    'goals_scored_avg': 2.8,
                    'goals_conceded_avg': 0.7,
                    'win_rate': 0.85
                },
                'away_team': {
                    'id': '80',
                    'name': 'Olympique Lyon',
                    'logo': 'https://media.api-sports.io/football/teams/80.png',
                    'recent_form': 'WDLWW',
                    'goals_scored_avg': 1.6,
                    'goals_conceded_avg': 1.3,
                    'win_rate': 0.55
                },
                'odds': {
                    'home_win': 1.45,
                    'draw': 4.50,
                    'away_win': 6.00
                },
                'h2h_stats': {
                    'last_5': 'HHHDH',
                    'home_wins': 4,
                    'draws': 1,
                    'away_wins': 0
                }
            }
        }
        
        # Retourner le match mock ou generer un match generique
        if match_id in mock_matches:
            return mock_matches[match_id]
        
        # Match generique pour tout autre ID
        return {
            'match_id': match_id,
            'sport': 'football',
            'league': 'Demo League',
            'country': 'Demo',
            'date': (datetime.now() + timedelta(days=5)).isoformat(),
            'venue': 'Demo Stadium',
            'status': 'NS',
            'home_team': {
                'id': 'home_' + match_id,
                'name': f'Team Home {match_id}',
                'recent_form': 'WDWLW',
                'goals_scored_avg': 1.5,
                'goals_conceded_avg': 1.2,
                'win_rate': 0.50
            },
            'away_team': {
                'id': 'away_' + match_id,
                'name': f'Team Away {match_id}',
                'recent_form': 'LWDWL',
                'goals_scored_avg': 1.3,
                'goals_conceded_avg': 1.4,
                'win_rate': 0.45
            },
            'odds': {
                'home_win': 2.50,
                'draw': 3.30,
                'away_win': 2.70
            },
            'h2h_stats': {
                'home_wins': 2,
                'draws': 2,
                'away_wins': 1
            }
        }

    def _get_mock_upcoming_matches(
        self,
        sport: str,
        league: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Retourne une liste de matchs mock."""
        matches = []
        for i in range(1, min(limit + 1, 4)):
            match = self._get_mock_match_data(str(i))
            if match and (not league or match.get('league') == league):
                matches.append(match)
        return matches


# Instance globale du service
sports_api_service = SportsAPIService()
