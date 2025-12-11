"""User model."""
from datetime import datetime
from app.core.database import db
from app.core.security import hash_password, verify_password


class User(db.Model):
    """User model for authentication and profile management."""
    
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    predictions = db.relationship("Prediction", back_populates="user", cascade="all, delete-orphan", lazy='dynamic')
    consultations = db.relationship("Consultation", back_populates="user", cascade="all, delete-orphan", lazy='dynamic')
    
    def set_password(self, password: str):
        """Hash and set user password using security module."""
        self.password_hash = hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash using security module."""
        return verify_password(password, self.password_hash)
    
    def update_last_login(self):
        """Update last login timestamp."""
        from datetime import datetime, timezone
        self.last_login = datetime.now(timezone.utc)
    
    def to_dict(self, include_stats=False):
        """Convert user to dictionary.
        
        Args:
            include_stats: Include user statistics (predictions count, etc.)
        """
        data = {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
        
        if include_stats:
            data['stats'] = {
                'total_predictions': self.predictions.count(),
                'total_consultations': self.consultations.count(),
                'sports_predictions': self.predictions.filter_by(prediction_type='sports').count(),
                'finance_predictions': self.predictions.filter_by(prediction_type='finance').count(),
            }
        
        return data
    
    def __repr__(self):
        return f"<User {self.username}>"
