"""
Schemas normalisés pour les données Sports et Finance.

Ces dataclasses définissent le contrat JSON entre:
- Les providers (mock ou réels)
- Les services métier (ML, predictions)
- L'API REST (frontend)

IMPORTANT: Tout changement ici doit être répercuté dans les tests contract.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================
# ENUMS
# ============================================

class MatchStatus(str, Enum):
    """Status d'un match sportif."""
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class TrendDirection(str, Enum):
    """Direction de tendance financière."""
    UP = "UP"
    DOWN = "DOWN"
    NEUTRAL = "NEUTRAL"


# ============================================
# SPORTS SCHEMAS
# ============================================

@dataclass
class SportsTeamNormalized:
    """Équipe sportive normalisée."""
    id: str
    name: str
    short_name: Optional[str] = None
    logo_url: Optional[str] = None
    country: Optional[str] = None
    
    # Stats récentes (optionnel)
    recent_form: Optional[str] = None  # Ex: "WWLDW"
    league_position: Optional[int] = None
    goals_scored: Optional[int] = None
    goals_conceded: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class SportsStatsNormalized:
    """Statistiques de match normalisées."""
    # Stats d'équipe domicile
    home_possession: Optional[float] = None
    home_shots: Optional[int] = None
    home_shots_on_target: Optional[int] = None
    home_corners: Optional[int] = None
    home_fouls: Optional[int] = None
    
    # Stats équipe extérieure
    away_possession: Optional[float] = None
    away_shots: Optional[int] = None
    away_shots_on_target: Optional[int] = None
    away_corners: Optional[int] = None
    away_fouls: Optional[int] = None
    
    # Head to head
    h2h_total_matches: Optional[int] = None
    h2h_home_wins: Optional[int] = None
    h2h_away_wins: Optional[int] = None
    h2h_draws: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class SportsMatchNormalized:
    """
    Match sportif normalisé.
    
    C'est le format UNIQUE renvoyé au frontend et consommé par le ML.
    Tous les providers (mock, API-Football, etc.) doivent mapper vers ce format.
    """
    # Identifiants
    match_id: str
    provider: str  # "mock", "api-football", "odds-api"
    
    # Équipes
    home_team: SportsTeamNormalized
    away_team: SportsTeamNormalized
    
    # Compétition
    competition: str
    competition_id: Optional[str] = None
    season: Optional[str] = None
    round: Optional[str] = None
    
    # Date et status
    date: datetime = field(default_factory=datetime.now)
    status: MatchStatus = MatchStatus.SCHEDULED
    
    # Score (si match terminé ou en cours)
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    
    # Statistiques détaillées
    stats: Optional[SportsStatsNormalized] = None
    
    # Cotes (optionnel)
    odds_home: Optional[float] = None
    odds_draw: Optional[float] = None
    odds_away: Optional[float] = None
    
    # Métadonnées
    venue: Optional[str] = None
    referee: Optional[str] = None
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire JSON-serializable."""
        result = {
            "match_id": self.match_id,
            "provider": self.provider,
            "home_team": self.home_team.to_dict(),
            "away_team": self.away_team.to_dict(),
            "competition": self.competition,
            "date": self.date.isoformat(),
            "status": self.status.value,
            "last_updated": self.last_updated.isoformat(),
        }
        
        # Ajouter les champs optionnels s'ils existent
        optional_fields = [
            'competition_id', 'season', 'round', 'home_score', 'away_score',
            'odds_home', 'odds_draw', 'odds_away', 'venue', 'referee'
        ]
        for field_name in optional_fields:
            value = getattr(self, field_name)
            if value is not None:
                result[field_name] = value
        
        if self.stats:
            result['stats'] = self.stats.to_dict()
        
        return result
    
    def to_ml_features(self) -> Dict[str, Any]:
        """
        Extrait les features pour le modèle ML.
        
        Returns:
            Dict avec les features numériques pour la prédiction.
        """
        features = {
            'home_team_id': self.home_team.id,
            'away_team_id': self.away_team.id,
        }
        
        # Features d'équipe
        if self.home_team.league_position:
            features['home_league_position'] = self.home_team.league_position
        if self.away_team.league_position:
            features['away_league_position'] = self.away_team.league_position
        
        # Features de cotes (indicateur important)
        if self.odds_home:
            features['odds_home'] = self.odds_home
        if self.odds_draw:
            features['odds_draw'] = self.odds_draw
        if self.odds_away:
            features['odds_away'] = self.odds_away
        
        # Stats si disponibles
        if self.stats:
            stats = self.stats
            if stats.h2h_total_matches:
                features['h2h_total'] = stats.h2h_total_matches
                if stats.h2h_home_wins:
                    features['h2h_home_win_rate'] = stats.h2h_home_wins / stats.h2h_total_matches
        
        return features


# ============================================
# FINANCE SCHEMAS
# ============================================

@dataclass
class FinancePricePoint:
    """Point de prix historique."""
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


@dataclass
class FinanceIndicatorsNormalized:
    """Indicateurs techniques normalisés."""
    # Moyennes mobiles
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    
    # Momentum
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    
    # Volatilité
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr_14: Optional[float] = None
    
    # Volume
    volume_sma_20: Optional[float] = None
    obv: Optional[float] = None
    
    # Tendance
    adx: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class FinanceAssetNormalized:
    """
    Actif financier normalisé.
    
    Format UNIQUE pour toutes les sources (yfinance, Alpha Vantage, mock).
    """
    # Identifiants
    symbol: str
    name: str
    provider: str  # "mock", "yfinance", "alphavantage"
    
    # Informations de base
    exchange: Optional[str] = None
    currency: str = "USD"
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    
    # Prix actuel
    current_price: float = 0.0
    previous_close: Optional[float] = None
    open_price: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    
    # Variation
    change: float = 0.0
    change_percent: float = 0.0
    
    # Volume
    volume: int = 0
    avg_volume: Optional[int] = None
    
    # Capitalisation
    market_cap: Optional[int] = None
    
    # Indicateurs techniques
    indicators: Optional[FinanceIndicatorsNormalized] = None
    
    # Historique des prix
    price_history: List[FinancePricePoint] = field(default_factory=list)
    
    # Métadonnées
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire JSON-serializable."""
        result = {
            "symbol": self.symbol,
            "name": self.name,
            "provider": self.provider,
            "currency": self.currency,
            "current_price": self.current_price,
            "change": self.change,
            "change_percent": self.change_percent,
            "volume": self.volume,
            "last_updated": self.last_updated.isoformat(),
        }
        
        # Champs optionnels
        optional_fields = [
            'exchange', 'sector', 'industry', 'country',
            'previous_close', 'open_price', 'day_high', 'day_low',
            'avg_volume', 'market_cap'
        ]
        for field_name in optional_fields:
            value = getattr(self, field_name)
            if value is not None:
                result[field_name] = value
        
        if self.indicators:
            result['indicators'] = self.indicators.to_dict()
        
        if self.price_history:
            result['price_history'] = [p.to_dict() for p in self.price_history[-30:]]  # Limiter à 30 points
        
        return result
    
    def to_ml_features(self) -> Dict[str, Any]:
        """
        Extrait les features pour le modèle ML.
        """
        features = {
            'symbol': self.symbol,
            'current_price': self.current_price,
            'change_percent': self.change_percent,
            'volume': self.volume,
        }
        
        if self.indicators:
            ind = self.indicators
            if ind.rsi_14:
                features['rsi_14'] = ind.rsi_14
            if ind.macd:
                features['macd'] = ind.macd
            if ind.sma_20:
                features['sma_20'] = ind.sma_20
            if ind.sma_50:
                features['sma_50'] = ind.sma_50
        
        return features


# ============================================
# VALIDATION HELPERS
# ============================================

def validate_sports_match(data: Dict[str, Any]) -> List[str]:
    """
    Valide qu'un dict contient les champs requis pour SportsMatchNormalized.
    
    Returns:
        Liste des erreurs (vide si valide).
    """
    errors = []
    required_fields = ['match_id', 'provider', 'home_team', 'away_team', 'competition', 'date']
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if 'home_team' in data and 'name' not in data['home_team']:
        errors.append("home_team must have 'name' field")
    if 'away_team' in data and 'name' not in data['away_team']:
        errors.append("away_team must have 'name' field")
    
    return errors


def validate_finance_asset(data: Dict[str, Any]) -> List[str]:
    """
    Valide qu'un dict contient les champs requis pour FinanceAssetNormalized.
    
    Returns:
        Liste des erreurs (vide si valide).
    """
    errors = []
    required_fields = ['symbol', 'name', 'provider', 'current_price']
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    return errors
