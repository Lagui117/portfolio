"""Consultation model for tracking user queries."""
from datetime import datetime
from app.core.database import db


class Consultation(db.Model):
    """Model to track user consultations and searches."""
    
    __tablename__ = "consultations"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Type: 'sports' or 'finance'
    consultation_type = db.Column(db.String(20), nullable=False, index=True)
    
    # Query details
    query_params = db.Column(db.Text)  # JSON string
    endpoint = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship("User", back_populates="consultations")
    
    def to_dict(self):
        """Convert consultation to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "consultation_type": self.consultation_type,
            "endpoint": self.endpoint,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<Consultation {self.id} - {self.consultation_type}>"
