"""
Schémas de données pour validation et typage.
Utilise des dataclasses Python pour typage fort et validation.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class UserRegistrationSchema:
    """Schéma pour l'inscription utilisateur."""
    email: str
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    def validate(self) -> None:
        """Valide les données."""
        from app.core.errors import ValidationError
        from app.core.security import validate_email, validate_password_strength
        
        if not self.email or not self.username or not self.password:
            raise ValidationError("Email, username and password are required")
        
        if not validate_email(self.email):
            raise ValidationError("Invalid email format")
        
        if len(self.username) < 3:
            raise ValidationError("Username must be at least 3 characters")
        
        is_valid, msg = validate_password_strength(self.password)
        if not is_valid:
            raise ValidationError(msg)


@dataclass
class UserLoginSchema:
    """Schéma pour la connexion utilisateur."""
    email: Optional[str] = None
    username: Optional[str] = None
    password: str = ''
    
    def validate(self) -> None:
        """Valide les données."""
        from app.core.errors import ValidationError
        
        if not (self.email or self.username):
            raise ValidationError("Email or username is required")
        if not self.password:
            raise ValidationError("Password is required")


@dataclass
class UserResponseSchema:
    """Schema de reponse pour les donnees utilisateur."""
    id: int
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_admin: bool
    role: str
    created_at: str
    last_login: Optional[str]
    
    @classmethod
    def from_model(cls, user):
        """Cree une instance depuis un modele User."""
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            role=user.role,
            created_at=user.created_at.isoformat() if user.created_at else None,
            last_login=user.last_login.isoformat() if user.last_login else None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return asdict(self)


@dataclass
class MatchInfoSchema:
    """Schéma pour les informations de match."""
    id: str
    home_team: str
    away_team: str
    competition: str
    date: Optional[str]
    venue: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None


@dataclass
class AssetInfoSchema:
    """Schéma pour les informations d'actif financier."""
    ticker: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    current_price: Optional[float] = None
    indicators: Optional[Dict[str, Any]] = None


@dataclass
class GPTAnalysisSchema:
    """Schéma pour l'analyse GPT."""
    domain: str
    summary: str
    analysis: str
    prediction_type: str
    prediction_value: Any
    confidence: float
    caveats: str
    educational_reminder: str
    ml_score: Optional[float] = None
    data_source: str = "gpt_analysis"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return asdict(self)


@dataclass
class SportsPredictionResponseSchema:
    """Schéma de réponse pour prédiction sportive."""
    match: MatchInfoSchema
    model_score: float
    gpt_analysis: GPTAnalysisSchema
    disclaimer: str = "Prediction experimentale a but educatif uniquement."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            "match": asdict(self.match),
            "model_score": self.model_score,
            "gpt_analysis": asdict(self.gpt_analysis),
            "disclaimer": self.disclaimer
        }


@dataclass
class FinancePredictionResponseSchema:
    """Schéma de réponse pour prédiction financière."""
    asset: AssetInfoSchema
    model_score: float
    gpt_analysis: GPTAnalysisSchema
    disclaimer: str = "Analyse experimentale a but educatif uniquement. Ne constitue pas un conseil d'investissement."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            "asset": asdict(self.asset),
            "model_score": self.model_score,
            "gpt_analysis": asdict(self.gpt_analysis),
            "disclaimer": self.disclaimer
        }


@dataclass
class PaginationSchema:
    """Schéma pour la pagination."""
    limit: int = 20
    offset: int = 0
    
    def validate(self) -> None:
        """Valide les paramètres de pagination."""
        from app.core.errors import ValidationError
        
        if self.limit < 1 or self.limit > 100:
            raise ValidationError("Limit must be between 1 and 100")
        
        if self.offset < 0:
            raise ValidationError("Offset must be non-negative")
