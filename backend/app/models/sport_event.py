"""
Modele SportEvent pour les evenements sportifs.
"""

from datetime import datetime, timezone
from app.core.database import db


class SportEvent(db.Model):
    """Modele pour les evenements sportifs."""
    
    __tablename__ = 'sport_events'
    
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), unique=True, nullable=True, index=True)
    
    # Informations du match
    sport_type = db.Column(db.String(50), default='football')
    league = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    
    # Equipes
    home_team = db.Column(db.String(100), nullable=False)
    away_team = db.Column(db.String(100), nullable=False)
    
    # Date et statut
    event_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, live, finished, cancelled
    
    # Resultats (apres le match)
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    
    # Cotes (optionnel)
    odds_home = db.Column(db.Float, nullable=True)
    odds_draw = db.Column(db.Float, nullable=True)
    odds_away = db.Column(db.Float, nullable=True)
    
    # Statistiques supplementaires (JSON)
    stats = db.Column(db.JSON, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relations
    predictions = db.relationship(
        'Prediction',
        back_populates='sport_event',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    def to_dict(self) -> dict:
        """Convertit l'evenement en dictionnaire."""
        return {
            'id': self.id,
            'external_id': self.external_id,
            'sport_type': self.sport_type,
            'league': self.league,
            'country': self.country,
            'home_team': self.home_team,
            'away_team': self.away_team,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'status': self.status,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'odds': {
                'home': self.odds_home,
                'draw': self.odds_draw,
                'away': self.odds_away,
            } if self.odds_home else None,
            'stats': self.stats,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<SportEvent {self.home_team} vs {self.away_team}>'
