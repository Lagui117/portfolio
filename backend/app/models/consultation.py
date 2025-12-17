"""
Modele Consultation pour tracer les consultations utilisateur.
"""

from datetime import datetime, timezone
from app.core.database import db


class Consultation(db.Model):
    """Modele pour les consultations (log d'utilisation)."""
    
    __tablename__ = 'consultations'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Utilisateur
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Type de consultation
    consultation_type = db.Column(db.String(20), nullable=False)  # 'sports' ou 'finance'
    
    # Details de la requete
    endpoint = db.Column(db.String(200), nullable=True)
    query_params = db.Column(db.JSON, nullable=True)
    
    # Resultat
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relations
    user = db.relationship('User', back_populates='consultations')
    
    def to_dict(self) -> dict:
        """Convertit la consultation en dictionnaire."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'consultation_type': self.consultation_type,
            'endpoint': self.endpoint,
            'query_params': self.query_params,
            'success': self.success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<Consultation {self.consultation_type} #{self.id}>'
