"""
Modèle Watchlist pour les favoris utilisateur.
Permet de suivre des équipes, ligues, tickers, etc.
"""

from datetime import datetime, timezone
from app.core.database import db


class Watchlist(db.Model):
    """Modèle pour les favoris/watchlist utilisateur."""
    
    __tablename__ = 'watchlists'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Utilisateur
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Type de favori
    item_type = db.Column(db.String(20), nullable=False)  # 'team', 'league', 'ticker', 'crypto'
    
    # Identifiants
    item_id = db.Column(db.String(100), nullable=False)  # ID ou symbole
    item_name = db.Column(db.String(200), nullable=False)  # Nom affichable
    
    # Métadonnées optionnelles
    item_data = db.Column(db.JSON, nullable=True)  # Données additionnelles (logo, pays, etc.)
    
    # Alertes
    alerts_enabled = db.Column(db.Boolean, default=False)
    alert_config = db.Column(db.JSON, nullable=True)  # Configuration des alertes
    
    # Notes utilisateur
    notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relations
    user = db.relationship('User', backref=db.backref('watchlist_items', lazy='dynamic'))
    
    # Contrainte unique: un user ne peut pas avoir le même item deux fois
    __table_args__ = (
        db.UniqueConstraint('user_id', 'item_type', 'item_id', name='unique_watchlist_item'),
    )
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            'id': self.id,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'item_data': self.item_data,
            'alerts_enabled': self.alerts_enabled,
            'alert_config': self.alert_config,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<Watchlist {self.item_type}:{self.item_name}>'
