"""
Modele Prediction pour stocker les predictions generees.
"""

from datetime import datetime, timezone
from app.core.database import db


class Prediction(db.Model):
    """Modele pour les predictions (sports et finance)."""
    
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Type de prediction
    prediction_type = db.Column(db.String(20), nullable=False)  # 'sports' ou 'finance'
    
    # Utilisateur
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # References (optionnelles)
    sport_event_id = db.Column(db.Integer, db.ForeignKey('sport_events.id'), nullable=True)
    stock_asset_id = db.Column(db.Integer, db.ForeignKey('stock_assets.id'), nullable=True)
    
    # Identifiants externes
    external_match_id = db.Column(db.String(100), nullable=True)
    ticker = db.Column(db.String(20), nullable=True)
    
    # Resultat de la prediction
    model_score = db.Column(db.Float, nullable=True)
    prediction_value = db.Column(db.String(100), nullable=True)  # ex: "HOME_WIN", "UP", "0.72"
    confidence = db.Column(db.Float, nullable=True)
    
    # Analyse GPT (stockee en JSON)
    gpt_analysis = db.Column(db.JSON, nullable=True)
    
    # Donnees d'entree (pour audit/debug)
    input_data = db.Column(db.JSON, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relations
    user = db.relationship('User', back_populates='predictions')
    sport_event = db.relationship('SportEvent', back_populates='predictions')
    stock_asset = db.relationship('StockAsset', back_populates='predictions')
    
    def to_dict(self) -> dict:
        """Convertit la prediction en dictionnaire."""
        return {
            'id': self.id,
            'prediction_type': self.prediction_type,
            'user_id': self.user_id,
            'external_match_id': self.external_match_id,
            'ticker': self.ticker,
            'model_score': self.model_score,
            'prediction_value': self.prediction_value,
            'confidence': self.confidence,
            'gpt_analysis': self.gpt_analysis,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<Prediction {self.prediction_type} #{self.id}>'
