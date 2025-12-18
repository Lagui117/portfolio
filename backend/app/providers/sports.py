"""
Sports Data Providers.

Providers disponibles:
- MockSportsProvider: Données simulées pour dev/tests
- RealSportsProvider: API-Football via RapidAPI

Sélection via env: USE_MOCK_SPORTS_API=true/false
"""

import os
import logging
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from app.providers.base import SportsDataProvider, with_retry, log_provider_call
from app.providers.schemas import (
    SportsMatchNormalized,
    SportsTeamNormalized,
    SportsStatsNormalized,
    MatchStatus,
)
from app.core.cache import cached

logger = logging.getLogger(__name__)


# ============================================
# MOCK SPORTS PROVIDER
# ============================================

class MockSportsProvider(SportsDataProvider):
    """
    Provider mock pour les données sportives.
    
    Génère des données réalistes pour le développement et les tests.
    """
    
    # Données de base pour générer des matchs réalistes
    TEAMS = {
        'ligue1': [
            {'id': 'psg', 'name': 'Paris Saint-Germain', 'short_name': 'PSG', 'country': 'France'},
            {'id': 'om', 'name': 'Olympique de Marseille', 'short_name': 'OM', 'country': 'France'},
            {'id': 'ol', 'name': 'Olympique Lyonnais', 'short_name': 'OL', 'country': 'France'},
            {'id': 'monaco', 'name': 'AS Monaco', 'short_name': 'ASM', 'country': 'France'},
            {'id': 'lille', 'name': 'LOSC Lille', 'short_name': 'LOSC', 'country': 'France'},
            {'id': 'nice', 'name': 'OGC Nice', 'short_name': 'OGCN', 'country': 'France'},
            {'id': 'lens', 'name': 'RC Lens', 'short_name': 'RCL', 'country': 'France'},
            {'id': 'rennes', 'name': 'Stade Rennais', 'short_name': 'SRFC', 'country': 'France'},
        ],
        'premier_league': [
            {'id': 'mancity', 'name': 'Manchester City', 'short_name': 'MCI', 'country': 'England'},
            {'id': 'arsenal', 'name': 'Arsenal FC', 'short_name': 'ARS', 'country': 'England'},
            {'id': 'liverpool', 'name': 'Liverpool FC', 'short_name': 'LIV', 'country': 'England'},
            {'id': 'chelsea', 'name': 'Chelsea FC', 'short_name': 'CHE', 'country': 'England'},
            {'id': 'manutd', 'name': 'Manchester United', 'short_name': 'MUN', 'country': 'England'},
            {'id': 'tottenham', 'name': 'Tottenham Hotspur', 'short_name': 'TOT', 'country': 'England'},
            {'id': 'newcastle', 'name': 'Newcastle United', 'short_name': 'NEW', 'country': 'England'},
            {'id': 'brighton', 'name': 'Brighton & Hove Albion', 'short_name': 'BHA', 'country': 'England'},
        ],
        'liga': [
            {'id': 'realmadrid', 'name': 'Real Madrid', 'short_name': 'RMA', 'country': 'Spain'},
            {'id': 'barcelona', 'name': 'FC Barcelona', 'short_name': 'BAR', 'country': 'Spain'},
            {'id': 'atletico', 'name': 'Atlético Madrid', 'short_name': 'ATM', 'country': 'Spain'},
            {'id': 'sevilla', 'name': 'Sevilla FC', 'short_name': 'SEV', 'country': 'Spain'},
        ],
        'champions_league': [
            {'id': 'bayern', 'name': 'Bayern Munich', 'short_name': 'BAY', 'country': 'Germany'},
            {'id': 'dortmund', 'name': 'Borussia Dortmund', 'short_name': 'BVB', 'country': 'Germany'},
            {'id': 'inter', 'name': 'Inter Milan', 'short_name': 'INT', 'country': 'Italy'},
            {'id': 'acmilan', 'name': 'AC Milan', 'short_name': 'MIL', 'country': 'Italy'},
        ],
    }
    
    COMPETITIONS = {
        'ligue1': 'Ligue 1',
        'premier_league': 'Premier League',
        'liga': 'La Liga',
        'champions_league': 'UEFA Champions League',
        'europa_league': 'UEFA Europa League',
    }
    
    def __init__(self):
        super().__init__('mock-sports')
        self._match_cache: Dict[str, SportsMatchNormalized] = {}
        self._initialize_matches()
        logger.info("MockSportsProvider initialized")
    
    def _initialize_matches(self):
        """Génère des matchs mock."""
        match_id = 1
        now = datetime.now()
        
        for comp_id, comp_name in self.COMPETITIONS.items():
            teams = self.TEAMS.get(comp_id, self.TEAMS['ligue1'])
            
            # Générer plusieurs matchs par compétition
            for i in range(0, len(teams) - 1, 2):
                for day_offset in [-1, 0, 1, 3, 7]:  # Passés, aujourd'hui, futurs
                    home_team = teams[i]
                    away_team = teams[i + 1]
                    
                    match_date = now + timedelta(days=day_offset, hours=random.randint(14, 21))
                    status = self._get_status_for_date(match_date, now)
                    
                    match = self._create_match(
                        match_id=f"mock_{match_id}",
                        home_team_data=home_team,
                        away_team_data=away_team,
                        competition=comp_name,
                        competition_id=comp_id,
                        match_date=match_date,
                        status=status
                    )
                    
                    self._match_cache[f"mock_{match_id}"] = match
                    match_id += 1
    
    def _get_status_for_date(self, match_date: datetime, now: datetime) -> MatchStatus:
        """Détermine le status basé sur la date."""
        diff = match_date - now
        hours_diff = diff.total_seconds() / 3600
        
        if hours_diff < -2:
            return MatchStatus.FINISHED
        elif -2 <= hours_diff <= 0:
            return MatchStatus.LIVE
        else:
            return MatchStatus.SCHEDULED
    
    def _create_match(
        self,
        match_id: str,
        home_team_data: Dict,
        away_team_data: Dict,
        competition: str,
        competition_id: str,
        match_date: datetime,
        status: MatchStatus
    ) -> SportsMatchNormalized:
        """Crée un match normalisé."""
        home_team = SportsTeamNormalized(
            id=home_team_data['id'],
            name=home_team_data['name'],
            short_name=home_team_data.get('short_name'),
            country=home_team_data.get('country'),
            recent_form=self._generate_form(),
            league_position=random.randint(1, 20),
            goals_scored=random.randint(15, 50),
            goals_conceded=random.randint(10, 40),
        )
        
        away_team = SportsTeamNormalized(
            id=away_team_data['id'],
            name=away_team_data['name'],
            short_name=away_team_data.get('short_name'),
            country=away_team_data.get('country'),
            recent_form=self._generate_form(),
            league_position=random.randint(1, 20),
            goals_scored=random.randint(15, 50),
            goals_conceded=random.randint(10, 40),
        )
        
        # Scores si match terminé ou en cours
        home_score = None
        away_score = None
        if status in [MatchStatus.FINISHED, MatchStatus.LIVE]:
            home_score = random.randint(0, 4)
            away_score = random.randint(0, 3)
        
        # Stats pour matchs terminés
        stats = None
        if status == MatchStatus.FINISHED:
            stats = SportsStatsNormalized(
                home_possession=random.uniform(40, 65),
                away_possession=100 - random.uniform(40, 65),
                home_shots=random.randint(8, 20),
                away_shots=random.randint(5, 18),
                home_shots_on_target=random.randint(2, 8),
                away_shots_on_target=random.randint(1, 7),
                h2h_total_matches=random.randint(5, 30),
                h2h_home_wins=random.randint(2, 15),
                h2h_away_wins=random.randint(2, 12),
                h2h_draws=random.randint(1, 8),
            )
        
        return SportsMatchNormalized(
            match_id=match_id,
            provider='mock',
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            competition_id=competition_id,
            date=match_date,
            status=status,
            home_score=home_score,
            away_score=away_score,
            stats=stats,
            odds_home=round(random.uniform(1.2, 4.0), 2),
            odds_draw=round(random.uniform(2.5, 4.5), 2),
            odds_away=round(random.uniform(1.5, 6.0), 2),
            venue=f"Stade {home_team.short_name or home_team.name}",
        )
    
    def _generate_form(self) -> str:
        """Génère une forme récente aléatoire."""
        results = ['W', 'D', 'L']
        return ''.join(random.choices(results, weights=[0.4, 0.3, 0.3], k=5))
    
    def health_check(self) -> Dict[str, Any]:
        """Health check du mock provider."""
        return {
            'healthy': True,
            'provider': 'MockSportsProvider',
            'matches_in_cache': len(self._match_cache)
        }
    
    def is_available(self) -> bool:
        """Mock provider toujours disponible."""
        return True
    
    def get_matches(self, league: Optional[str] = None) -> List[SportsMatchNormalized]:
        """Raccourci pour list_matches avec filtre par league."""
        return self.list_matches(competition=league)
    
    @log_provider_call
    def get_match(self, match_id: str) -> Optional[SportsMatchNormalized]:
        """Récupère un match par ID."""
        # Normaliser l'ID
        if not match_id.startswith('mock_'):
            match_id = f"mock_{match_id}"
        
        return self._match_cache.get(match_id)
    
    @log_provider_call
    def list_matches(
        self,
        competition: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[SportsMatchNormalized]:
        """Liste les matchs avec filtres."""
        matches = list(self._match_cache.values())
        
        # Filtrer par compétition
        if competition:
            matches = [m for m in matches if competition.lower() in m.competition.lower()]
        
        # Filtrer par status
        if status:
            try:
                status_enum = MatchStatus(status.lower())
                matches = [m for m in matches if m.status == status_enum]
            except ValueError:
                pass
        
        # Trier par date
        matches.sort(key=lambda m: m.date)
        
        return matches[:limit]
    
    @log_provider_call
    def get_live_matches(self) -> List[SportsMatchNormalized]:
        """Récupère les matchs en cours."""
        return [m for m in self._match_cache.values() if m.status == MatchStatus.LIVE]


# ============================================
# REAL SPORTS PROVIDER (API-Football)
# ============================================

class RealSportsProvider(SportsDataProvider):
    """
    Provider réel utilisant API-Football (RapidAPI).
    
    Nécessite:
    - SPORTS_API_KEY: Clé RapidAPI
    - SPORTS_API_HOST: Host de l'API (défaut: api-football-v1.p.rapidapi.com)
    """
    
    BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
    
    def __init__(self):
        super().__init__('api-football')
        self.api_key = os.getenv('SPORTS_API_KEY', '')
        self.api_host = os.getenv('SPORTS_API_HOST', 'api-football-v1.p.rapidapi.com')
        self._session = None
        
        if not self.api_key:
            logger.warning("SPORTS_API_KEY not set. RealSportsProvider will fail on requests.")
    
    def _get_session(self):
        """Lazy init de la session requests."""
        if self._session is None:
            try:
                import requests
                self._session = requests.Session()
                self._session.headers.update({
                    'X-RapidAPI-Key': self.api_key,
                    'X-RapidAPI-Host': self.api_host,
                })
            except ImportError:
                raise RuntimeError("requests library not available")
        return self._session
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie la connectivité API."""
        if not self.api_key:
            return {
                'healthy': False,
                'provider': 'RealSportsProvider',
                'error': 'API key not configured'
            }
        try:
            session = self._get_session()
            response = session.get(f"{self.BASE_URL}/status", timeout=5)
            return {
                'healthy': response.status_code == 200,
                'provider': 'RealSportsProvider',
                'status_code': response.status_code
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'healthy': False,
                'provider': 'RealSportsProvider',
                'error': str(e)
            }
    
    def is_available(self) -> bool:
        """Vérifie si le provider est disponible."""
        return bool(self.api_key)
    
    @cached(ttl=120, key_prefix="sports_real")
    @with_retry(max_attempts=3, backoff_factor=1.5, timeout=5.0)
    @log_provider_call
    def get_match(self, match_id: str) -> Optional[SportsMatchNormalized]:
        """Récupère un match depuis l'API."""
        session = self._get_session()
        
        response = session.get(
            f"{self.BASE_URL}/fixtures",
            params={'id': match_id},
            timeout=5
        )
        response.raise_for_status()
        
        data = response.json()
        if not data.get('response'):
            return None
        
        return self._map_fixture_to_normalized(data['response'][0])
    
    @cached(ttl=300, key_prefix="sports_list")
    @with_retry(max_attempts=2, backoff_factor=1.0, timeout=10.0)
    @log_provider_call
    def list_matches(
        self,
        competition: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[SportsMatchNormalized]:
        """Liste les matchs depuis l'API."""
        session = self._get_session()
        
        params = {}
        if competition:
            params['league'] = competition
        if date_from:
            params['from'] = date_from
        if date_to:
            params['to'] = date_to
        
        response = session.get(
            f"{self.BASE_URL}/fixtures",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        matches = [self._map_fixture_to_normalized(f) for f in data.get('response', [])]
        
        return matches[:limit]
    
    @log_provider_call
    def get_live_matches(self) -> List[SportsMatchNormalized]:
        """Récupère les matchs en cours."""
        session = self._get_session()
        
        response = session.get(
            f"{self.BASE_URL}/fixtures",
            params={'live': 'all'},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        return [self._map_fixture_to_normalized(f) for f in data.get('response', [])]
    
    def _map_fixture_to_normalized(self, fixture: Dict) -> SportsMatchNormalized:
        """Mappe une fixture API-Football vers le format normalisé."""
        teams = fixture.get('teams', {})
        goals = fixture.get('goals', {})
        fixture_info = fixture.get('fixture', {})
        league = fixture.get('league', {})
        
        # Mapper les équipes
        home_data = teams.get('home', {})
        away_data = teams.get('away', {})
        
        home_team = SportsTeamNormalized(
            id=str(home_data.get('id', '')),
            name=home_data.get('name', 'Unknown'),
            logo_url=home_data.get('logo'),
        )
        
        away_team = SportsTeamNormalized(
            id=str(away_data.get('id', '')),
            name=away_data.get('name', 'Unknown'),
            logo_url=away_data.get('logo'),
        )
        
        # Mapper le status
        status_short = fixture_info.get('status', {}).get('short', 'NS')
        status_map = {
            'NS': MatchStatus.SCHEDULED,
            'TBD': MatchStatus.SCHEDULED,
            '1H': MatchStatus.LIVE,
            'HT': MatchStatus.LIVE,
            '2H': MatchStatus.LIVE,
            'FT': MatchStatus.FINISHED,
            'AET': MatchStatus.FINISHED,
            'PEN': MatchStatus.FINISHED,
            'PST': MatchStatus.POSTPONED,
            'CANC': MatchStatus.CANCELLED,
        }
        status = status_map.get(status_short, MatchStatus.SCHEDULED)
        
        # Parser la date
        date_str = fixture_info.get('date', '')
        try:
            match_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            match_date = datetime.now()
        
        return SportsMatchNormalized(
            match_id=str(fixture_info.get('id', '')),
            provider='api-football',
            home_team=home_team,
            away_team=away_team,
            competition=league.get('name', 'Unknown'),
            competition_id=str(league.get('id', '')),
            season=str(league.get('season', '')),
            round=league.get('round'),
            date=match_date,
            status=status,
            home_score=goals.get('home'),
            away_score=goals.get('away'),
            venue=fixture_info.get('venue', {}).get('name'),
            referee=fixture_info.get('referee'),
        )


# ============================================
# FACTORY FUNCTION
# ============================================

_sports_provider_instance: Optional[SportsDataProvider] = None


def get_sports_provider() -> SportsDataProvider:
    """
    Factory pour obtenir le provider sports configuré.
    
    Sélection basée sur USE_MOCK_SPORTS_API:
    - true (défaut): MockSportsProvider
    - false: RealSportsProvider (nécessite SPORTS_API_KEY)
    
    Returns:
        Instance singleton du provider
    """
    global _sports_provider_instance
    
    if _sports_provider_instance is None:
        use_mock = os.getenv('USE_MOCK_SPORTS_API', 'true').lower() == 'true'
        
        if use_mock:
            _sports_provider_instance = MockSportsProvider()
        else:
            # Vérifier que les credentials sont disponibles
            if not os.getenv('SPORTS_API_KEY'):
                logger.warning(
                    "SPORTS_API_KEY not set, falling back to MockSportsProvider"
                )
                _sports_provider_instance = MockSportsProvider()
            else:
                _sports_provider_instance = RealSportsProvider()
        
        logger.info(f"Sports provider initialized: {_sports_provider_instance.provider_name}")
    
    return _sports_provider_instance


def reset_sports_provider():
    """Reset le singleton (utile pour les tests)."""
    global _sports_provider_instance
    _sports_provider_instance = None
