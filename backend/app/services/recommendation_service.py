"""
RecommendationService - Moteur de recommandation "Next Best Action".

Analyse l'état courant (données live, alertes, focus) et détermine
la meilleure action à entreprendre.

Principes:
- 1 action prioritaire claire
- Maximum 2 actions secondaires
- Justification concise pour chaque recommandation
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ActionType:
    """Types d'actions recommandées."""
    OPEN_ANALYSIS = "OPEN_ANALYSIS"
    ADD_WATCHLIST = "ADD_WATCHLIST"
    REVIEW_ALERT = "REVIEW_ALERT"
    CHECK_PREDICTION = "CHECK_PREDICTION"
    MONITOR = "MONITOR"
    REFRESH_DATA = "REFRESH_DATA"
    VIEW_DETAILS = "VIEW_DETAILS"


class Urgency:
    """Niveaux d'urgence."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Category:
    """Catégories de recommandation."""
    SPORTS = "SPORTS"
    FINANCE = "FINANCE"
    SYSTEM = "SYSTEM"


class RecommendationService:
    """
    Service de recommandation Next Best Action.
    
    Analyse le contexte utilisateur et génère des recommandations
    actionnables basées sur les règles de décision.
    """
    
    # Seuils de décision
    THRESHOLDS = {
        'critical_price_change': 5.0,      # % variation prix critique
        'high_price_change': 3.0,          # % variation prix élevée
        'critical_odds_change': 0.5,       # Variation cotes critique
        'high_odds_change': 0.3,           # Variation cotes élevée
        'high_confidence': 0.75,           # Confiance IA élevée
        'very_high_confidence': 0.85,      # Confiance IA très élevée
        'match_soon_minutes': 60,          # Match imminent (minutes)
        'match_urgent_minutes': 30,        # Match très proche
        'stale_data_minutes': 10,          # Données obsolètes
    }
    
    def __init__(self):
        self.rules = self._build_rules()
    
    def _build_rules(self) -> List[Dict]:
        """Construit la liste des règles de décision ordonnées par priorité."""
        return [
            # Règles CRITICAL (priorité 1)
            {
                'name': 'critical_alert',
                'priority': 1,
                'condition': self._check_critical_alert,
                'builder': self._build_critical_action,
            },
            {
                'name': 'extreme_volatility',
                'priority': 2,
                'condition': self._check_extreme_volatility,
                'builder': self._build_volatility_action,
            },
            {
                'name': 'match_starting_soon',
                'priority': 3,
                'condition': self._check_match_starting,
                'builder': self._build_match_action,
            },
            
            # Règles OPPORTUNITY (priorité 4-6)
            {
                'name': 'high_confidence_opportunity',
                'priority': 4,
                'condition': self._check_high_confidence,
                'builder': self._build_opportunity_action,
            },
            {
                'name': 'odds_movement',
                'priority': 5,
                'condition': self._check_odds_movement,
                'builder': self._build_odds_action,
            },
            {
                'name': 'price_movement',
                'priority': 6,
                'condition': self._check_price_movement,
                'builder': self._build_price_action,
            },
            
            # Règles WARNING (priorité 7-8)
            {
                'name': 'warning_alert',
                'priority': 7,
                'condition': self._check_warning_alert,
                'builder': self._build_warning_action,
            },
            {
                'name': 'stale_data',
                'priority': 8,
                'condition': self._check_stale_data,
                'builder': self._build_refresh_action,
            },
            
            # Règle par défaut (priorité 99)
            {
                'name': 'monitor_default',
                'priority': 99,
                'condition': lambda *args: True,  # Toujours vrai
                'builder': self._build_monitor_action,
            },
        ]
    
    def get_next_best_action(
        self,
        user_id: int,
        live_data: Dict[str, Any],
        alerts: List[Dict],
        focus_item: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Détermine la meilleure action à entreprendre.
        
        Args:
            user_id: ID de l'utilisateur
            live_data: Données live (sports, finance, kpis)
            alerts: Liste des alertes actives
            focus_item: Élément actuellement en focus (optionnel)
        
        Returns:
            Dictionnaire avec primary action et secondary actions
        """
        context = {
            'user_id': user_id,
            'live_data': live_data or {},
            'alerts': alerts or [],
            'focus_item': focus_item,
            'sports': live_data.get('sports', []) if live_data else [],
            'finance': live_data.get('finance', []) if live_data else [],
            'timestamp': datetime.now(timezone.utc),
        }
        
        primary_action = None
        secondary_actions = []
        
        # Parcourir les règles par priorité
        for rule in sorted(self.rules, key=lambda r: r['priority']):
            try:
                result = rule['condition'](context)
                if result:
                    action = rule['builder'](context, result)
                    if action:
                        if primary_action is None:
                            primary_action = action
                            primary_action['type'] = 'PRIMARY'
                        elif len(secondary_actions) < 2:
                            action['type'] = 'SECONDARY'
                            secondary_actions.append(action)
            except Exception as e:
                logger.warning(f"Erreur règle {rule['name']}: {e}")
                continue
        
        # Fallback si aucune action trouvée
        if primary_action is None:
            primary_action = self._build_monitor_action(context, None)
            primary_action['type'] = 'PRIMARY'
        
        return {
            'primary': primary_action,
            'secondary': secondary_actions,
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'context_summary': self._build_context_summary(context),
        }
    
    # ============================================
    # Conditions de règles
    # ============================================
    
    def _check_critical_alert(self, context: Dict) -> Optional[Dict]:
        """Vérifie s'il y a une alerte CRITICAL active."""
        for alert in context.get('alerts', []):
            if alert.get('level') == 'critical' or alert.get('type') == 'critical':
                return alert
        return None
    
    def _check_warning_alert(self, context: Dict) -> Optional[Dict]:
        """Vérifie s'il y a une alerte WARNING non traitée."""
        for alert in context.get('alerts', []):
            level = alert.get('level') or alert.get('type')
            if level == 'warning' and not alert.get('acknowledged'):
                return alert
        return None
    
    def _check_extreme_volatility(self, context: Dict) -> Optional[Dict]:
        """Vérifie une volatilité extrême sur les actifs finance."""
        for asset in context.get('finance', []):
            change = abs(asset.get('changePercent') or asset.get('change_percent') or 0)
            if change >= self.THRESHOLDS['critical_price_change']:
                return {
                    'asset': asset,
                    'change': change,
                    'type': 'finance',
                }
        return None
    
    def _check_price_movement(self, context: Dict) -> Optional[Dict]:
        """Vérifie un mouvement de prix significatif."""
        for asset in context.get('finance', []):
            change = abs(asset.get('changePercent') or asset.get('change_percent') or 0)
            confidence = asset.get('confidence') or 0
            if change >= self.THRESHOLDS['high_price_change'] and confidence >= 0.6:
                return {
                    'asset': asset,
                    'change': change,
                    'confidence': confidence,
                    'type': 'finance',
                }
        return None
    
    def _check_match_starting(self, context: Dict) -> Optional[Dict]:
        """Vérifie si un match commence bientôt."""
        for match in context.get('sports', []):
            minutes = match.get('minutesToStart') or match.get('minutes_to_start')
            if minutes is not None and 0 < minutes <= self.THRESHOLDS['match_urgent_minutes']:
                return {
                    'match': match,
                    'minutes': minutes,
                    'type': 'sports',
                }
        return None
    
    def _check_odds_movement(self, context: Dict) -> Optional[Dict]:
        """Vérifie un mouvement de cotes significatif."""
        for match in context.get('sports', []):
            odds_change = abs(match.get('oddsChange') or match.get('odds_change') or 0)
            if odds_change >= self.THRESHOLDS['high_odds_change']:
                return {
                    'match': match,
                    'odds_change': odds_change,
                    'type': 'sports',
                }
        return None
    
    def _check_high_confidence(self, context: Dict) -> Optional[Dict]:
        """Vérifie s'il y a une prédiction haute confiance."""
        # Chercher d'abord dans focus_item
        focus = context.get('focus_item')
        if focus:
            confidence = focus.get('confidence') or 0
            if confidence >= self.THRESHOLDS['very_high_confidence']:
                return {'item': focus, 'confidence': confidence, 'source': 'focus'}
        
        # Chercher dans finance
        for asset in context.get('finance', []):
            confidence = asset.get('confidence') or 0
            if confidence >= self.THRESHOLDS['very_high_confidence']:
                return {'item': asset, 'confidence': confidence, 'source': 'finance'}
        
        # Chercher dans sports
        for match in context.get('sports', []):
            confidence = match.get('confidence') or 0
            if confidence >= self.THRESHOLDS['high_confidence']:
                return {'item': match, 'confidence': confidence, 'source': 'sports'}
        
        return None
    
    def _check_stale_data(self, context: Dict) -> Optional[Dict]:
        """Vérifie si les données sont obsolètes."""
        live_data = context.get('live_data', {})
        last_update = live_data.get('lastUpdate') or live_data.get('last_update')
        
        if last_update:
            try:
                if isinstance(last_update, str):
                    last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                diff = (context['timestamp'] - last_update).total_seconds() / 60
                if diff >= self.THRESHOLDS['stale_data_minutes']:
                    return {'minutes_stale': diff}
            except Exception:
                pass
        
        return None
    
    # ============================================
    # Builders d'actions
    # ============================================
    
    def _build_critical_action(self, context: Dict, result: Dict) -> Dict:
        """Construit une action pour alerte critique."""
        alert = result
        target_type = alert.get('data', {}).get('type', 'UNKNOWN')
        target_id = alert.get('data', {}).get('id') or alert.get('id')
        
        return {
            'category': Category.SYSTEM,
            'title': alert.get('title', 'Alerte critique'),
            'reason': alert.get('message', 'Action immédiate requise'),
            'confidence': 0.95,
            'urgency': Urgency.HIGH,
            'recommended_action': ActionType.REVIEW_ALERT,
            'target': {
                'type': target_type.upper(),
                'id': str(target_id),
            },
            'cta_label': 'Voir maintenant',
            'cta_route': alert.get('action', {}).get('route', '/app/central'),
        }
    
    def _build_volatility_action(self, context: Dict, result: Dict) -> Dict:
        """Construit une action pour volatilité extrême."""
        asset = result['asset']
        symbol = asset.get('symbol', 'N/A')
        change = result['change']
        direction = 'hausse' if asset.get('changePercent', 0) > 0 else 'baisse'
        
        return {
            'category': Category.FINANCE,
            'title': f'Analyser {symbol}',
            'reason': f'Volatilité extrême détectée: {direction} de {change:.1f}%',
            'confidence': 0.88,
            'urgency': Urgency.HIGH,
            'recommended_action': ActionType.OPEN_ANALYSIS,
            'target': {
                'type': 'TICKER',
                'id': symbol,
            },
            'cta_label': 'Voir l\'analyse',
            'cta_route': f'/app/finance?ticker={symbol}',
        }
    
    def _build_match_action(self, context: Dict, result: Dict) -> Dict:
        """Construit une action pour match imminent."""
        match = result['match']
        minutes = result['minutes']
        home = match.get('homeTeam') or match.get('home_team', 'Équipe A')
        away = match.get('awayTeam') or match.get('away_team', 'Équipe B')
        match_id = match.get('id') or match.get('matchId')
        confidence = match.get('confidence', 0)
        
        urgency = Urgency.HIGH if minutes <= 15 else Urgency.MEDIUM
        
        return {
            'category': Category.SPORTS,
            'title': f'{home} vs {away}',
            'reason': f'Coup d\'envoi dans {minutes} min' + (f' • Confiance {confidence*100:.0f}%' if confidence else ''),
            'confidence': confidence or 0.7,
            'urgency': urgency,
            'recommended_action': ActionType.CHECK_PREDICTION,
            'target': {
                'type': 'MATCH',
                'id': str(match_id),
            },
            'cta_label': 'Voir la prédiction',
            'cta_route': f'/app/sports?match={match_id}',
        }
    
    def _build_opportunity_action(self, context: Dict, result: Dict) -> Dict:
        """Construit une action pour opportunité haute confiance."""
        item = result['item']
        confidence = result['confidence']
        source = result['source']
        
        if source == 'finance' or item.get('symbol'):
            symbol = item.get('symbol', 'N/A')
            prediction = item.get('prediction', '')
            return {
                'category': Category.FINANCE,
                'title': f'Opportunité sur {symbol}',
                'reason': f'Prédiction IA à {confidence*100:.0f}% de confiance' + (f' • {prediction}' if prediction else ''),
                'confidence': confidence,
                'urgency': Urgency.MEDIUM,
                'recommended_action': ActionType.OPEN_ANALYSIS,
                'target': {
                    'type': 'TICKER',
                    'id': symbol,
                },
                'cta_label': 'Analyser',
                'cta_route': f'/app/finance?ticker={symbol}',
            }
        else:
            home = item.get('homeTeam') or item.get('home_team', 'Match')
            away = item.get('awayTeam') or item.get('away_team', '')
            match_id = item.get('id') or item.get('matchId')
            title = f'{home} vs {away}' if away else home
            
            return {
                'category': Category.SPORTS,
                'title': f'Opportunité: {title}',
                'reason': f'Prédiction IA à {confidence*100:.0f}% de confiance',
                'confidence': confidence,
                'urgency': Urgency.MEDIUM,
                'recommended_action': ActionType.CHECK_PREDICTION,
                'target': {
                    'type': 'MATCH',
                    'id': str(match_id),
                },
                'cta_label': 'Voir l\'analyse',
                'cta_route': f'/app/sports?match={match_id}',
            }
    
    def _build_odds_action(self, context: Dict, result: Dict) -> Dict:
        """Construit une action pour mouvement de cotes."""
        match = result['match']
        odds_change = result['odds_change']
        home = match.get('homeTeam') or match.get('home_team', 'Équipe A')
        away = match.get('awayTeam') or match.get('away_team', 'Équipe B')
        match_id = match.get('id') or match.get('matchId')
        
        return {
            'category': Category.SPORTS,
            'title': f'Réévaluer {home} vs {away}',
            'reason': f'Mouvement de cotes détecté ({odds_change:+.2f})',
            'confidence': 0.72,
            'urgency': Urgency.MEDIUM,
            'recommended_action': ActionType.CHECK_PREDICTION,
            'target': {
                'type': 'MATCH',
                'id': str(match_id),
            },
            'cta_label': 'Réévaluer',
            'cta_route': f'/app/sports?match={match_id}',
        }
    
    def _build_price_action(self, context: Dict, result: Dict) -> Dict:
        """Construit une action pour mouvement de prix."""
        asset = result['asset']
        symbol = asset.get('symbol', 'N/A')
        change = result['change']
        confidence = result['confidence']
        direction = '📈' if asset.get('changePercent', 0) > 0 else '📉'
        
        return {
            'category': Category.FINANCE,
            'title': f'{direction} Analyser {symbol}',
            'reason': f'Variation de {change:.1f}% avec {confidence*100:.0f}% de confiance IA',
            'confidence': confidence,
            'urgency': Urgency.MEDIUM,
            'recommended_action': ActionType.OPEN_ANALYSIS,
            'target': {
                'type': 'TICKER',
                'id': symbol,
            },
            'cta_label': 'Analyser',
            'cta_route': f'/app/finance?ticker={symbol}',
        }
    
    def _build_warning_action(self, context: Dict, result: Dict) -> Dict:
        """Construit une action pour alerte warning."""
        alert = result
        
        return {
            'category': Category.SYSTEM,
            'title': alert.get('title', 'Avertissement'),
            'reason': alert.get('message', 'Vérification recommandée'),
            'confidence': 0.65,
            'urgency': Urgency.MEDIUM,
            'recommended_action': ActionType.REVIEW_ALERT,
            'target': {
                'type': 'ALERT',
                'id': str(alert.get('id', 'unknown')),
            },
            'cta_label': 'Vérifier',
            'cta_route': alert.get('action', {}).get('route', '/app/central'),
        }
    
    def _build_refresh_action(self, context: Dict, result: Dict) -> Dict:
        """Construit une action pour rafraîchir les données."""
        minutes = result.get('minutes_stale', 10)
        
        return {
            'category': Category.SYSTEM,
            'title': 'Actualiser les données',
            'reason': f'Données non mises à jour depuis {int(minutes)} min',
            'confidence': 0.5,
            'urgency': Urgency.LOW,
            'recommended_action': ActionType.REFRESH_DATA,
            'target': {
                'type': 'SYSTEM',
                'id': 'refresh',
            },
            'cta_label': 'Rafraîchir',
            'cta_route': None,  # Action locale
        }
    
    def _build_monitor_action(self, context: Dict, result: Any) -> Dict:
        """Construit une action de surveillance par défaut."""
        sports_count = len(context.get('sports', []))
        finance_count = len(context.get('finance', []))
        
        if sports_count > 0 or finance_count > 0:
            reason = f'{sports_count} match(s) et {finance_count} actif(s) sous surveillance'
        else:
            reason = 'Aucun événement majeur détecté'
        
        return {
            'category': Category.SYSTEM,
            'title': 'Continuer la surveillance',
            'reason': reason,
            'confidence': 0.5,
            'urgency': Urgency.LOW,
            'recommended_action': ActionType.MONITOR,
            'target': {
                'type': 'SYSTEM',
                'id': 'monitor',
            },
            'cta_label': 'Explorer',
            'cta_route': '/app/central',
        }
    
    def _build_context_summary(self, context: Dict) -> Dict:
        """Construit un résumé du contexte analysé."""
        return {
            'sports_count': len(context.get('sports', [])),
            'finance_count': len(context.get('finance', [])),
            'alerts_count': len(context.get('alerts', [])),
            'has_focus': context.get('focus_item') is not None,
            'critical_alerts': sum(
                1 for a in context.get('alerts', []) 
                if a.get('level') == 'critical' or a.get('type') == 'critical'
            ),
        }


# Singleton pour réutilisation
_recommendation_service = None

def get_recommendation_service() -> RecommendationService:
    """Retourne l'instance singleton du service."""
    global _recommendation_service
    if _recommendation_service is None:
        _recommendation_service = RecommendationService()
    return _recommendation_service
