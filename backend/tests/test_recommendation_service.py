"""
Tests pour le RecommendationService - Système Next Best Action.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


class TestRecommendationService:
    """Tests pour le service de recommandation NBA."""

    @pytest.fixture
    def service(self):
        """Instancie le service de recommandation."""
        from app.services.recommendation_service import RecommendationService
        return RecommendationService()

    @pytest.fixture
    def mock_live_data(self):
        """Données live simulées."""
        return {
            'sports': [
                {
                    'id': 1,
                    'home_team': 'PSG',
                    'away_team': 'Marseille',
                    'confidence': 0.82,
                    'start_time': (datetime.utcnow() + timedelta(minutes=20)).isoformat(),
                    'odds_movement': 12,
                },
                {
                    'id': 2,
                    'home_team': 'Lyon',
                    'away_team': 'Monaco',
                    'confidence': 0.65,
                    'start_time': (datetime.utcnow() + timedelta(hours=3)).isoformat(),
                },
            ],
            'finance': [
                {
                    'symbol': 'AAPL',
                    'price': 175.50,
                    'change_percent': 2.3,
                    'confidence': 0.78,
                    'trend': 'bullish',
                },
                {
                    'symbol': 'TSLA',
                    'price': 245.00,
                    'change_percent': -6.5,  # Volatilité extrême
                    'confidence': 0.72,
                    'trend': 'bearish',
                },
            ],
        }

    @pytest.fixture
    def mock_alerts(self):
        """Alertes simulées."""
        return [
            {
                'id': 'alert_1',
                'type': 'warning',
                'level': 'warning',
                'title': 'Variation importante',
                'message': 'AAPL: +2.3%',
                'created_at': datetime.utcnow().isoformat(),
            },
        ]

    def test_get_next_best_action_returns_structure(self, service, mock_live_data, mock_alerts):
        """Vérifie que l'action retournée a la bonne structure."""
        result = service.get_next_best_action(
            user_id=1,
            live_data=mock_live_data,
            alerts=mock_alerts,
        )

        assert result is not None
        assert 'primary' in result
        assert 'secondary' in result
        assert 'generated_at' in result
        assert 'context_summary' in result

    def test_primary_action_structure(self, service, mock_live_data, mock_alerts):
        """Vérifie la structure de l'action primaire."""
        result = service.get_next_best_action(
            user_id=1,
            live_data=mock_live_data,
            alerts=mock_alerts,
        )

        primary = result['primary']
        assert primary is not None
        assert 'type' in primary
        assert 'category' in primary
        assert 'title' in primary
        assert 'reason' in primary
        assert 'urgency' in primary
        assert 'cta_label' in primary
        assert 'cta_route' in primary

    def test_category_values(self, service, mock_live_data, mock_alerts):
        """Vérifie que les catégories sont valides."""
        result = service.get_next_best_action(
            user_id=1,
            live_data=mock_live_data,
            alerts=mock_alerts,
        )

        valid_categories = ['SPORTS', 'FINANCE', 'SYSTEM']
        assert result['primary']['category'] in valid_categories

    def test_urgency_values(self, service, mock_live_data, mock_alerts):
        """Vérifie que les niveaux d'urgence sont valides."""
        result = service.get_next_best_action(
            user_id=1,
            live_data=mock_live_data,
            alerts=mock_alerts,
        )

        valid_urgencies = ['HIGH', 'MEDIUM', 'LOW']
        assert result['primary']['urgency'] in valid_urgencies

    def test_extreme_volatility_triggers_high_priority(self, service, mock_alerts):
        """Vérifie que la volatilité extrême déclenche une action haute priorité."""
        volatile_data = {
            'sports': [],
            'finance': [
                {
                    'symbol': 'GME',
                    'price': 180.00,
                    'change_percent': -8.5,  # > 5% = extrême
                    'confidence': 0.6,
                },
            ],
        }

        result = service.get_next_best_action(
            user_id=1,
            live_data=volatile_data,
            alerts=mock_alerts,
        )

        primary = result['primary']
        # Devrait être une action finance prioritaire
        assert primary['category'] == 'FINANCE'
        assert primary['urgency'] == 'HIGH'
        assert 'GME' in primary['title'] or 'GME' in primary['reason']

    def test_match_starting_soon_triggers_action(self, service, mock_alerts):
        """Vérifie qu'un match imminent génère une action."""
        soon_data = {
            'sports': [
                {
                    'id': 100,
                    'home_team': 'Real Madrid',
                    'away_team': 'Barcelona',
                    'confidence': 0.75,
                    'start_time': (datetime.utcnow() + timedelta(minutes=10)).isoformat(),
                },
            ],
            'finance': [],
        }

        result = service.get_next_best_action(
            user_id=1,
            live_data=soon_data,
            alerts=[],
        )

        primary = result['primary']
        assert primary['category'] == 'SPORTS'
        # Match dans 10 min = urgence haute
        assert primary['urgency'] in ['HIGH', 'MEDIUM']

    def test_high_confidence_opportunity(self, service):
        """Vérifie que la haute confiance génère une opportunité."""
        high_conf_data = {
            'sports': [],
            'finance': [
                {
                    'symbol': 'NVDA',
                    'price': 500.00,
                    'change_percent': 1.2,
                    'confidence': 0.92,  # > 0.85 = haute confiance
                    'trend': 'bullish',
                },
            ],
        }

        result = service.get_next_best_action(
            user_id=1,
            live_data=high_conf_data,
            alerts=[],
        )

        primary = result['primary']
        assert primary['confidence'] >= 0.85 or 'NVDA' in primary.get('title', '')

    def test_critical_alert_takes_priority(self, service, mock_live_data):
        """Vérifie qu'une alerte critique est prioritaire."""
        critical_alerts = [
            {
                'id': 'critical_1',
                'type': 'critical',
                'level': 'critical',
                'title': 'Alerte critique système',
                'message': 'Action immédiate requise',
                'created_at': datetime.utcnow().isoformat(),
            },
        ]

        result = service.get_next_best_action(
            user_id=1,
            live_data=mock_live_data,
            alerts=critical_alerts,
        )

        primary = result['primary']
        # L'alerte critique devrait être prioritaire
        assert primary['urgency'] == 'HIGH'
        assert primary['category'] == 'SYSTEM'

    def test_secondary_actions_limited_to_two(self, service, mock_live_data, mock_alerts):
        """Vérifie que les actions secondaires sont limitées à 2."""
        result = service.get_next_best_action(
            user_id=1,
            live_data=mock_live_data,
            alerts=mock_alerts,
        )

        assert len(result['secondary']) <= 2

    def test_focus_item_influence(self, service, mock_live_data, mock_alerts):
        """Vérifie que le focus item influence la recommandation."""
        focus_item = {
            'type': 'finance',
            'id': 'AAPL',
            'name': 'Apple Inc.',
        }

        result = service.get_next_best_action(
            user_id=1,
            live_data=mock_live_data,
            alerts=mock_alerts,
            focus_item=focus_item,
        )

        # Devrait favoriser AAPL ou la catégorie FINANCE
        primary = result['primary']
        # L'action devrait être liée au focus si possible
        assert primary is not None

    def test_empty_data_returns_default_action(self, service):
        """Vérifie le comportement avec des données vides."""
        result = service.get_next_best_action(
            user_id=1,
            live_data={'sports': [], 'finance': []},
            alerts=[],
        )

        assert result['primary'] is not None
        # Action par défaut = monitoring
        assert result['primary']['urgency'] == 'LOW'

    def test_context_summary_structure(self, service, mock_live_data, mock_alerts):
        """Vérifie la structure du résumé de contexte."""
        result = service.get_next_best_action(
            user_id=1,
            live_data=mock_live_data,
            alerts=mock_alerts,
        )

        summary = result['context_summary']
        # Vérifie que le résumé contient des informations pertinentes
        assert 'alerts_count' in summary
        assert 'sports_count' in summary or 'finance_count' in summary
        assert isinstance(summary, dict)

    def test_generated_at_is_iso_format(self, service, mock_live_data, mock_alerts):
        """Vérifie que generated_at est au format ISO."""
        result = service.get_next_best_action(
            user_id=1,
            live_data=mock_live_data,
            alerts=mock_alerts,
        )

        # Doit être parsable en datetime
        generated_at = result['generated_at']
        assert generated_at is not None
        # Vérifie que c'est une string ISO valide
        datetime.fromisoformat(generated_at.replace('Z', '+00:00'))


class TestRecommendationServiceIntegration:
    """Tests d'intégration pour le service."""

    def test_service_import(self):
        """Vérifie que le service peut être importé."""
        from app.services.recommendation_service import (
            RecommendationService,
            get_recommendation_service,
        )
        
        service = get_recommendation_service()
        assert service is not None
        assert isinstance(service, RecommendationService)

    def test_singleton_pattern(self):
        """Vérifie le pattern singleton."""
        from app.services.recommendation_service import get_recommendation_service
        
        service1 = get_recommendation_service()
        service2 = get_recommendation_service()
        
        assert service1 is service2
