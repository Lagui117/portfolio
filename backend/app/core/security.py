"""
Utilitaires de securite pour l'authentification.
Hashage de mot de passe et gestion JWT.
"""

import re
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple

import bcrypt
import jwt
from flask import current_app

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt.
    
    Args:
        password: Mot de passe en clair.
    
    Returns:
        Mot de passe hashe.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifie un mot de passe contre son hash.
    
    Args:
        plain_password: Mot de passe en clair.
        hashed_password: Mot de passe hashe.
    
    Returns:
        True si le mot de passe correspond.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f'Erreur verification mot de passe: {e}')
        return False


def create_access_token(
    user_id: int, 
    role: str = 'user',
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cree un token JWT avec le role de l'utilisateur.
    
    Args:
        user_id: ID de l'utilisateur.
        role: Role de l'utilisateur (user/admin).
        expires_delta: Duree de validite du token.
    
    Returns:
        Token JWT.
    """
    if expires_delta is None:
        expires_delta = current_app.config.get(
            'JWT_ACCESS_TOKEN_EXPIRES',
            timedelta(hours=1)
        )
    
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': expire,
        'iat': now,
        'type': 'access'
    }
    
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def create_refresh_token(
    user_id: int,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crée un refresh token JWT.
    
    Args:
        user_id: ID de l'utilisateur.
        expires_delta: Durée de validité du token (défaut: 30 jours).
    
    Returns:
        Refresh token JWT.
    """
    if expires_delta is None:
        expires_delta = current_app.config.get(
            'JWT_REFRESH_TOKEN_EXPIRES',
            timedelta(days=30)
        )
    
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    
    payload = {
        'user_id': user_id,
        'exp': expire,
        'iat': now,
        'type': 'refresh'
    }
    
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode et verifie un token JWT.
    
    Args:
        token: Token JWT.
    
    Returns:
        Payload du token si valide, None sinon.
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        # Vérifier que c'est bien un access token
        if payload.get('type') != 'access':
            logger.warning('Token type mismatch: expected access token')
            return None
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning('Token expire')
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f'Token invalide: {e}')
        return None


def decode_refresh_token(token: str) -> Optional[dict]:
    """
    Decode et vérifie un refresh token JWT.
    
    Args:
        token: Refresh token JWT.
    
    Returns:
        Payload du token si valide, None sinon.
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        # Vérifier que c'est bien un refresh token
        if payload.get('type') != 'refresh':
            logger.warning('Token type mismatch: expected refresh token')
            return None
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning('Refresh token expiré')
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f'Refresh token invalide: {e}')
        return None


def get_token_remaining_time(token: str) -> Optional[int]:
    """
    Récupère le temps restant avant expiration d'un token.
    
    Args:
        token: Token JWT.
    
    Returns:
        Secondes restantes, ou None si invalide/expiré.
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256'],
            options={'verify_exp': False}  # Ne pas lever d'exception si expiré
        )
        exp = payload.get('exp')
        if exp:
            now = datetime.now(timezone.utc).timestamp()
            remaining = int(exp - now)
            return max(0, remaining)
        return None
    except jwt.InvalidTokenError:
        return None


def validate_email(email: str) -> bool:
    """
    Valide le format d'une adresse email.
    
    Args:
        email: Adresse email.
    
    Returns:
        True si le format est valide.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Verifie la force d'un mot de passe.
    
    Args:
        password: Mot de passe a verifier.
    
    Returns:
        Tuple (valide, message d'erreur).
    """
    if len(password) < 8:
        return False, 'Le mot de passe doit contenir au moins 8 caracteres.'
    
    if not re.search(r'[A-Z]', password):
        return False, 'Le mot de passe doit contenir au moins une majuscule.'
    
    if not re.search(r'[a-z]', password):
        return False, 'Le mot de passe doit contenir au moins une minuscule.'
    
    if not re.search(r'\d', password):
        return False, 'Le mot de passe doit contenir au moins un chiffre.'
    
    return True, ''
