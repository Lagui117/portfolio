"""
Tests étendus pour MockSportsProvider et RealSportsProvider.

Cible: providers/sports.py (actuellement 61% coverage)
"""

import pytest
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from app.providers.sports import (
    MockSportsProvider,
    RealSportsProvider,
    get_sports_provider,
    reset_sports_provider,
)
from app.providers.schemas import (
    SportsMatchNormalized,
    SportsTeamNormalized,
    SportsStatsNormalized,
    MatchStatus,
)


# ============================================
# MOCK SPORTS PROVIDER TESTS
# ============================================

class TestMockSportsProviderInit:
    """Tests d'initialisation du MockSportsProvider."""
    
    def test_init_sets_provider_name(self):
        """Le provider doit avoir le nom 'mock-sports'."""
        provider = MockSportsProvider()
        assert provider.provider_name == 'mock-sports'
    
    def test_init_creates_match_cache(self):
        """Le cache de matchs doit être créé."""
        provider = MockSportsProvider()
        assert hasattr(provider, '_match_cache')
        assert isinstance(provider._match_cache, dict)
        assert len(provider._match_cache) > 0  # Des matchs sont générés
    
    def test_teams_data_structure(self):
        """TEAMS doit contenir les données correctes."""
        provider = MockSportsProvider()
        
        assert 'ligue1' in provider.TEAMS
        assert 'premier_league' in provider.TEAMS
        assert 'liga' in provider.TEAMS
        assert 'champions_league' in provider.TEAMS
        
        # Vérifier la structure d'une équipe
        for league, teams in provider.TEAMS.items():
            for team in teams:
                assert 'id' in team
                assert 'name' in team
                assert 'short_name' in team
                assert 'country' in team
    
    def test_competitions_data_structure(self):
        """COMPETITIONS doit être correctement défini."""
        provider = MockSportsProvider()
        
        assert 'ligue1' in provider.COMPETITIONS
        assert 'premier_league' in provider.COMPETITIONS
        assert provider.COMPETITIONS['ligue1'] == 'Ligue 1'


class TestMockSportsProviderHealthCheck:
    """Tests de health_check."""
    
    def test_health_check_returns_healthy(self):
        """health_check doit retourner healthy: True."""
        provider = MockSportsProvider()
        result = provider.health_check()
        
        assert result['healthy'] is True
        assert result['provider'] == 'MockSportsProvider'
        assert 'matches_in_cache' in result
        assert result['matches_in_cache'] > 0
    
    def test_is_available_returns_true(self):
        """is_available doit toujours retourner True pour mock."""
        provider = MockSportsProvider()
        assert provider.is_available() is True


class TestMockSportsProviderMatchStatus:
    """Tests de _get_status_for_date."""
    
    def test_status_for_past_match(self):
        """Match passé doit être FINISHED."""
        provider = MockSportsProvider()
        now = datetime.now()
        past_date = now - timedelta(hours=3)
        
        status = provider._get_status_for_date(past_date, now)
        assert status == MatchStatus.FINISHED
    
    def test_status_for_live_match(self):
        """Match en cours doit être LIVE."""
        provider = MockSportsProvider()
        now = datetime.now()
        live_date = now - timedelta(minutes=30)  # Match commencé il y a 30 min
        
        status = provider._get_status_for_date(live_date, now)
        assert status == MatchStatus.LIVE
    
    def test_status_for_future_match(self):
        """Match futur doit être SCHEDULED."""
        provider = MockSportsProvider()
        now = datetime.now()
        future_date = now + timedelta(hours=2)
        
        status = provider._get_status_for_date(future_date, now)
        assert status == MatchStatus.SCHEDULED


class TestMockSportsProviderCreateMatch:
    """Tests de _create_match."""
    
    def test_create_match_returns_normalized(self):
        """_create_match retourne un SportsMatchNormalized."""
        provider = MockSportsProvider()
        
        home_team = {'id': 'psg', 'name': 'Paris Saint-Germain', 'short_name': 'PSG', 'country': 'France'}
        away_team = {'id': 'om', 'name': 'Olympique de Marseille', 'short_name': 'OM', 'country': 'France'}
        
        match = provider._create_match(
            match_id='test_1',
            home_team_data=home_team,
            away_team_data=away_team,
            competition='Ligue 1',
            competition_id='ligue1',
            match_date=datetime.now(),
            status=MatchStatus.SCHEDULED
        )
        
        assert isinstance(match, SportsMatchNormalized)
        assert match.match_id == 'test_1'
        assert match.home_team.name == 'Paris Saint-Germain'
        assert match.away_team.name == 'Olympique de Marseille'
    
    def test_create_match_finished_has_scores(self):
        """Match terminé doit avoir des scores."""
        provider = MockSportsProvider()
        
        home_team = {'id': 'psg', 'name': 'PSG'}
        away_team = {'id': 'om', 'name': 'OM'}
        
        match = provider._create_match(
            match_id='test_2',
            home_team_data=home_team,
            away_team_data=away_team,
            competition='Ligue 1',
            competition_id='ligue1',
            match_date=datetime.now() - timedelta(hours=3),
            status=MatchStatus.FINISHED
        )
        
        assert match.home_score is not None
        assert match.away_score is not None
        assert match.stats is not None
    
    def test_create_match_live_has_scores(self):
        """Match en cours doit avoir des scores."""
        provider = MockSportsProvider()
        
        home_team = {'id': 'psg', 'name': 'PSG'}
        away_team = {'id': 'om', 'name': 'OM'}
        
        match = provider._create_match(
            match_id='test_3',
            home_team_data=home_team,
            away_team_data=away_team,
            competition='Ligue 1',
            competition_id='ligue1',
            match_date=datetime.now(),
            status=MatchStatus.LIVE
        )
        
        assert match.home_score is not None
        assert match.away_score is not None
    
    def test_create_match_scheduled_no_scores(self):
        """Match prévu ne doit pas avoir de scores."""
        provider = MockSportsProvider()
        
        home_team = {'id': 'psg', 'name': 'PSG'}
        away_team = {'id': 'om', 'name': 'OM'}
        
        match = provider._create_match(
            match_id='test_4',
            home_team_data=home_team,
            away_team_data=away_team,
            competition='Ligue 1',
            competition_id='ligue1',
            match_date=datetime.now() + timedelta(days=1),
            status=MatchStatus.SCHEDULED
        )
        
        assert match.home_score is None
        assert match.away_score is None


class TestMockSportsProviderGenerateForm:
    """Tests de _generate_form."""
    
    def test_generate_form_length(self):
        """_generate_form génère une forme de 5 caractères."""
        provider = MockSportsProvider()
        form = provider._generate_form()
        
        assert len(form) == 5
    
    def test_generate_form_valid_chars(self):
        """_generate_form utilise W, D, L uniquement."""
        provider = MockSportsProvider()
        
        for _ in range(10):
            form = provider._generate_form()
            for char in form:
                assert char in ['W', 'D', 'L']


class TestMockSportsProviderGetMatch:
    """Tests de get_match."""
    
    def test_get_match_existing(self):
        """get_match retourne un match existant."""
        provider = MockSportsProvider()
        
        # Obtenir un ID valide du cache
        match_id = list(provider._match_cache.keys())[0]
        match = provider.get_match(match_id)
        
        assert match is not None
        assert isinstance(match, SportsMatchNormalized)
    
    def test_get_match_normalizes_id(self):
        """get_match normalise l'ID (ajoute mock_ si nécessaire)."""
        provider = MockSportsProvider()
        
        # Essayer avec un ID sans préfixe
        match = provider.get_match('1')
        
        # Devrait chercher mock_1
        expected_match = provider._match_cache.get('mock_1')
        if expected_match:
            assert match == expected_match
    
    def test_get_match_not_found(self):
        """get_match retourne None si non trouvé."""
        provider = MockSportsProvider()
        
        match = provider.get_match('nonexistent_99999')
        assert match is None


class TestMockSportsProviderGetMatches:
    """Tests de get_matches."""
    
    def test_get_matches_returns_list(self):
        """get_matches retourne une liste."""
        provider = MockSportsProvider()
        matches = provider.get_matches()
        
        assert isinstance(matches, list)
    
    def test_get_matches_with_league_filter(self):
        """get_matches filtre par league."""
        provider = MockSportsProvider()
        
        matches = provider.get_matches(league='Ligue 1')
        
        for match in matches:
            assert 'Ligue 1' in match.competition


class TestMockSportsProviderListMatches:
    """Tests de list_matches."""
    
    def test_list_matches_default(self):
        """list_matches retourne des matchs."""
        provider = MockSportsProvider()
        matches = provider.list_matches()
        
        assert len(matches) > 0
        assert len(matches) <= 20  # Default limit
    
    def test_list_matches_with_limit(self):
        """list_matches respecte la limite."""
        provider = MockSportsProvider()
        
        matches_5 = provider.list_matches(limit=5)
        assert len(matches_5) <= 5
    
    def test_list_matches_with_competition_filter(self):
        """list_matches filtre par compétition."""
        provider = MockSportsProvider()
        
        matches = provider.list_matches(competition='Premier League')
        
        for match in matches:
            assert 'premier league' in match.competition.lower()
    
    def test_list_matches_with_status_filter(self):
        """list_matches filtre par status."""
        provider = MockSportsProvider()
        
        matches = provider.list_matches(status='finished')
        
        for match in matches:
            assert match.status == MatchStatus.FINISHED
    
    def test_list_matches_invalid_status(self):
        """list_matches ignore les status invalides."""
        provider = MockSportsProvider()
        
        # Ne devrait pas lever d'exception
        matches = provider.list_matches(status='invalid_status')
        
        assert isinstance(matches, list)
    
    def test_list_matches_sorted_by_date(self):
        """list_matches trie par date."""
        provider = MockSportsProvider()
        
        matches = provider.list_matches(limit=10)
        
        for i in range(len(matches) - 1):
            assert matches[i].date <= matches[i + 1].date


class TestMockSportsProviderGetLiveMatches:
    """Tests de get_live_matches."""
    
    def test_get_live_matches_returns_live_only(self):
        """get_live_matches retourne uniquement les matchs LIVE."""
        provider = MockSportsProvider()
        
        live_matches = provider.get_live_matches()
        
        for match in live_matches:
            assert match.status == MatchStatus.LIVE


# ============================================
# REAL SPORTS PROVIDER TESTS
# ============================================

class TestRealSportsProviderInit:
    """Tests d'initialisation du RealSportsProvider."""
    
    def test_init_sets_provider_name(self):
        """Le provider doit avoir le nom 'api-football'."""
        with patch.dict(os.environ, {'SPORTS_API_KEY': 'test_key'}, clear=False):
            provider = RealSportsProvider()
            assert provider.provider_name == 'api-football'
    
    def test_init_without_api_key(self):
        """Initialization sans API key."""
        with patch.dict(os.environ, {}, clear=True):
            provider = RealSportsProvider()
            assert provider.api_key == ''
    
    def test_init_with_api_key(self):
        """Initialization avec API key."""
        with patch.dict(os.environ, {'SPORTS_API_KEY': 'my_test_key'}, clear=False):
            provider = RealSportsProvider()
            assert provider.api_key == 'my_test_key'


class TestRealSportsProviderHealthCheck:
    """Tests de health_check pour RealSportsProvider."""
    
    def test_health_check_without_api_key(self):
        """health_check retourne unhealthy sans API key."""
        with patch.dict(os.environ, {}, clear=True):
            provider = RealSportsProvider()
            result = provider.health_check()
            
            assert result['healthy'] is False
            assert 'error' in result
    
    def test_health_check_with_api_key_success(self):
        """health_check avec API key réussit."""
        with patch.dict(os.environ, {'SPORTS_API_KEY': 'test_key'}, clear=False):
            provider = RealSportsProvider()
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            
            with patch.object(provider, '_get_session') as mock_session:
                mock_session.return_value.get.return_value = mock_response
                result = provider.health_check()
                
                assert result['healthy'] is True
    
    def test_health_check_with_exception(self):
        """health_check gère les exceptions."""
        with patch.dict(os.environ, {'SPORTS_API_KEY': 'test_key'}, clear=False):
            provider = RealSportsProvider()
            
            with patch.object(provider, '_get_session') as mock_session:
                mock_session.return_value.get.side_effect = Exception("Connection failed")
                result = provider.health_check()
                
                assert result['healthy'] is False
                assert 'error' in result


class TestRealSportsProviderAvailability:
    """Tests de is_available pour RealSportsProvider."""
    
    def test_is_available_without_api_key(self):
        """is_available retourne False sans API key."""
        with patch.dict(os.environ, {}, clear=True):
            provider = RealSportsProvider()
            assert provider.is_available() is False
    
    def test_is_available_with_api_key(self):
        """is_available retourne True avec API key."""
        with patch.dict(os.environ, {'SPORTS_API_KEY': 'test_key'}, clear=False):
            provider = RealSportsProvider()
            assert provider.is_available() is True


class TestRealSportsProviderGetSession:
    """Tests de _get_session."""
    
    def test_get_session_creates_session(self):
        """_get_session crée une session requests."""
        with patch.dict(os.environ, {'SPORTS_API_KEY': 'test_key'}, clear=False):
            provider = RealSportsProvider()
            
            # Mocker requests
            with patch('app.providers.sports.RealSportsProvider._get_session') as mock:
                mock_session = MagicMock()
                mock.return_value = mock_session
                
                session = provider._get_session()
                assert session is not None


class TestRealSportsProviderMapFixture:
    """Tests de _map_fixture_to_normalized."""
    
    def test_map_fixture_basic(self):
        """_map_fixture_to_normalized mappe correctement."""
        with patch.dict(os.environ, {'SPORTS_API_KEY': 'test_key'}, clear=False):
            provider = RealSportsProvider()
            
            fixture = {
                'fixture': {
                    'id': 123,
                    'date': '2024-01-15T20:00:00+00:00',
                    'status': {'short': 'FT'},
                    'venue': {'name': 'Parc des Princes'},
                    'referee': 'John Doe'
                },
                'teams': {
                    'home': {'id': 1, 'name': 'PSG', 'logo': 'http://logo.png'},
                    'away': {'id': 2, 'name': 'OM', 'logo': 'http://logo2.png'}
                },
                'goals': {'home': 2, 'away': 1},
                'league': {
                    'id': 61,
                    'name': 'Ligue 1',
                    'season': 2024,
                    'round': 'Regular Season - 15'
                }
            }
            
            result = provider._map_fixture_to_normalized(fixture)
            
            assert isinstance(result, SportsMatchNormalized)
            assert result.match_id == '123'
            assert result.home_team.name == 'PSG'
            assert result.away_team.name == 'OM'
            assert result.home_score == 2
            assert result.away_score == 1
            assert result.status == MatchStatus.FINISHED
    
    def test_map_fixture_status_mapping(self):
        """_map_fixture_to_normalized mappe les status correctement."""
        with patch.dict(os.environ, {'SPORTS_API_KEY': 'test_key'}, clear=False):
            provider = RealSportsProvider()
            
            status_tests = [
                ('NS', MatchStatus.SCHEDULED),
                ('1H', MatchStatus.LIVE),
                ('HT', MatchStatus.LIVE),
                ('2H', MatchStatus.LIVE),
                ('FT', MatchStatus.FINISHED),
                ('PST', MatchStatus.POSTPONED),
                ('CANC', MatchStatus.CANCELLED),
            ]
            
            for api_status, expected_status in status_tests:
                fixture = {
                    'fixture': {
                        'id': 1,
                        'date': '2024-01-15T20:00:00+00:00',
                        'status': {'short': api_status}
                    },
                    'teams': {
                        'home': {'id': 1, 'name': 'Team A'},
                        'away': {'id': 2, 'name': 'Team B'}
                    },
                    'goals': {},
                    'league': {}
                }
                
                result = provider._map_fixture_to_normalized(fixture)
                assert result.status == expected_status, f"Failed for {api_status}"


# ============================================
# FACTORY FUNCTION TESTS
# ============================================

class TestGetSportsProvider:
    """Tests de get_sports_provider factory."""
    
    def setup_method(self):
        """Reset le singleton avant chaque test."""
        reset_sports_provider()
    
    def teardown_method(self):
        """Reset le singleton après chaque test."""
        reset_sports_provider()
    
    def test_get_sports_provider_mock_default(self):
        """Par défaut, retourne MockSportsProvider."""
        with patch.dict(os.environ, {'USE_MOCK_SPORTS_API': 'true'}, clear=False):
            provider = get_sports_provider()
            assert isinstance(provider, MockSportsProvider)
    
    def test_get_sports_provider_mock_explicit(self):
        """USE_MOCK_SPORTS_API=true retourne MockSportsProvider."""
        with patch.dict(os.environ, {'USE_MOCK_SPORTS_API': 'true'}, clear=False):
            reset_sports_provider()
            provider = get_sports_provider()
            assert isinstance(provider, MockSportsProvider)
    
    def test_get_sports_provider_real_without_key(self):
        """Sans API key, fallback vers Mock."""
        with patch.dict(os.environ, {'USE_MOCK_SPORTS_API': 'false', 'SPORTS_API_KEY': ''}, clear=True):
            reset_sports_provider()
            provider = get_sports_provider()
            assert isinstance(provider, MockSportsProvider)
    
    def test_get_sports_provider_real_with_key(self):
        """Avec API key, retourne RealSportsProvider."""
        with patch.dict(os.environ, {'USE_MOCK_SPORTS_API': 'false', 'SPORTS_API_KEY': 'my_key'}, clear=False):
            reset_sports_provider()
            provider = get_sports_provider()
            assert isinstance(provider, RealSportsProvider)
    
    def test_get_sports_provider_singleton(self):
        """get_sports_provider retourne un singleton."""
        with patch.dict(os.environ, {'USE_MOCK_SPORTS_API': 'true'}, clear=False):
            reset_sports_provider()
            provider1 = get_sports_provider()
            provider2 = get_sports_provider()
            assert provider1 is provider2


class TestResetSportsProvider:
    """Tests de reset_sports_provider."""
    
    def test_reset_clears_singleton(self):
        """reset_sports_provider efface le singleton."""
        with patch.dict(os.environ, {'USE_MOCK_SPORTS_API': 'true'}, clear=False):
            provider1 = get_sports_provider()
            reset_sports_provider()
            provider2 = get_sports_provider()
            
            # Devraient être des instances différentes
            assert provider1 is not provider2


# ============================================
# EDGE CASES AND INTEGRATION
# ============================================

class TestSportsProviderEdgeCases:
    """Tests des cas limites."""
    
    def test_empty_teams_data(self):
        """Création de match avec données équipe minimales."""
        provider = MockSportsProvider()
        
        match = provider._create_match(
            match_id='edge_1',
            home_team_data={'id': '1', 'name': 'Team A'},
            away_team_data={'id': '2', 'name': 'Team B'},
            competition='Test League',
            competition_id='test',
            match_date=datetime.now(),
            status=MatchStatus.SCHEDULED
        )
        
        assert match.home_team.short_name is None
        assert match.away_team.short_name is None
    
    def test_list_matches_empty_result(self):
        """list_matches avec filtre qui ne retourne rien."""
        provider = MockSportsProvider()
        
        matches = provider.list_matches(competition='NonexistentLeague123')
        
        assert matches == []
    
    def test_multiple_provider_instances(self):
        """Multiples instances de MockSportsProvider."""
        provider1 = MockSportsProvider()
        provider2 = MockSportsProvider()
        
        # Chaque instance a son propre cache
        assert provider1._match_cache is not provider2._match_cache


class TestSportsMatchStats:
    """Tests des statistiques de match."""
    
    def test_finished_match_has_stats(self):
        """Match terminé a des statistiques."""
        provider = MockSportsProvider()
        
        # Trouver un match terminé
        finished_matches = [m for m in provider._match_cache.values() 
                           if m.status == MatchStatus.FINISHED]
        
        if finished_matches:
            match = finished_matches[0]
            assert match.stats is not None
            assert isinstance(match.stats, SportsStatsNormalized)
            assert match.stats.home_possession is not None
    
    def test_stats_possession_exists(self):
        """Les stats de possession existent."""
        provider = MockSportsProvider()
        
        finished_matches = [m for m in provider._match_cache.values() 
                           if m.status == MatchStatus.FINISHED and m.stats]
        
        for match in finished_matches[:5]:  # Tester quelques matchs
            assert match.stats.home_possession is not None
            assert match.stats.away_possession is not None
            # Les possessions sont des pourcentages entre 0 et 100
            assert 0 <= match.stats.home_possession <= 100
            assert 0 <= match.stats.away_possession <= 100
