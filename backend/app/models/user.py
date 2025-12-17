"""
Modele User pour l'authentification et le profil utilisateur.
Gere les roles (user / admin) et les permissions.
"""

from datetime import datetime, timezone
from app.core.database import db
from app.core.security import hash_password, verify_password


class UserRole:
    """Constantes pour les roles utilisateur."""
    USER = 'user'
    ADMIN = 'admin'
    
    @classmethod
    def all_roles(cls):
        return [cls.USER, cls.ADMIN]


class User(db.Model):
    """Modele utilisateur avec gestion des roles."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profil
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    
    # Roles et permissions
    role = db.Column(db.String(20), default=UserRole.USER, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    @property
    def is_admin(self):
        """Verifie si l'utilisateur est admin."""
        return self.role == UserRole.ADMIN
    
    def make_admin(self):
        """Promouvoir en admin."""
        self.role = UserRole.ADMIN
    
    def revoke_admin(self):
        """Revoquer les droits admin."""
        self.role = UserRole.USER
    
    # Relations
    predictions = db.relationship(
        'Prediction',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    consultations = db.relationship(
        'Consultation',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    def set_password(self, password: str):
        """Hash et definit le mot de passe."""
        self.password_hash = hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """Verifie le mot de passe."""
        return verify_password(password, self.password_hash)
    
    def update_last_login(self):
        """Met a jour la date de derniere connexion."""
        self.last_login = datetime.now(timezone.utc)
    
    def to_dict(self, include_stats: bool = False, include_admin_info: bool = False) -> dict:
        """
        Convertit l'utilisateur en dictionnaire.
        
        Args:
            include_stats: Inclure les statistiques d'utilisation.
            include_admin_info: Inclure les infos admin (email, role).
        
        Returns:
            Dictionnaire des donnees utilisateur.
        """
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
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
        return f'<User {self.username} ({self.role})>'
