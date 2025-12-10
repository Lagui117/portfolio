"""Prediction model."""
from datetime import datetime
from app.core.database import db


class Prediction(db.Model):
    """Model to store ML predictions made by users."""
    
    __tablename__ = "predictions"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Type: 'sports' or 'finance'
    prediction_type = db.Column(db.String(20), nullable=False, index=True)
    
    # Input data (stored as JSON string)
    input_data = db.Column(db.Text, nullable=False)
    
    # Prediction result
    prediction_result = db.Column(db.String(100), nullable=False)
    confidence_score = db.Column(db.Float)
    
    # Model metadata
    model_version = db.Column(db.String(50))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship("User", back_populates="predictions")
    
    def to_dict(self):
        """Convert prediction to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "prediction_type": self.prediction_type,
            "prediction_result": self.prediction_result,
            "confidence_score": self.confidence_score,
            "model_version": self.model_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<Prediction {self.id} - {self.prediction_type}>"
