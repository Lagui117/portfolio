"""
Endpoints d'authentification.
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me
- PUT /api/v1/auth/me (mise a jour profil)
- PUT /api/v1/auth/password (changement mot de passe)
"""

import logging
from functools import wraps
from typing import Callable
from flask import Blueprint, request, jsonify

from app.core.database import db
from app.core.security import (
    create_access_token, 
    create_refresh_token,
    decode_access_token, 
    decode_refresh_token,
    get_token_remaining_time
)
from app.core.errors import (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError
)
from app.core.schemas import (
    UserRegistrationSchema,
    UserLoginSchema,
    UserResponseSchema
)
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

# Blueprint
auth_bp = Blueprint('auth', __name__)


def token_required(f: Callable) -> Callable:
    """
    Decorateur pour proteger les routes avec JWT.
    Injecte current_user dans la fonction decoree.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Extraire le token du header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                raise ValidationError(
                    "Invalid Authorization header format. Use: Bearer <token>"
                )
        
        if not token:
            raise AuthenticationError("Missing authentication token")
        
        # Decoder le token
        payload = decode_access_token(token)
        if not payload:
            raise AuthenticationError("Invalid or expired token")
        
        # Recuperer l'utilisateur
        current_user = db.session.get(User, payload['user_id'])
        if not current_user or not current_user.is_active:
            raise AuthenticationError("User account not found or inactive")
        
        return f(current_user=current_user, *args, **kwargs)
    
    return decorated


def admin_required(f: Callable) -> Callable:
    """
    Decorateur pour restreindre l'acces aux admins.
    Doit etre utilise APRES @token_required.
    """
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            raise AuthorizationError("Admin access required")
        return f(current_user=current_user, *args, **kwargs)
    
    return decorated


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Inscription d'un nouvel utilisateur.
    
    Request JSON:
        {
            "email": "string",
            "username": "string",
            "password": "string",
            "first_name": "string" (optionnel),
            "last_name": "string" (optionnel)
        }
    
    Returns:
        201: Utilisateur cree avec access_token
        400: Erreur de validation
    """
    data = request.get_json()
    
    if not data:
        raise ValidationError("JSON data required")
    
    # Valider et créer le schéma
    try:
        schema = UserRegistrationSchema(**data)
        schema.validate()
    except TypeError as e:
        raise ValidationError(f"Invalid request data: {str(e)}")
    
    # Vérification unicité email
    if User.query.filter_by(email=schema.email.lower()).first():
        raise ValidationError("Email already in use")
    
    # Vérification unicité username
    if User.query.filter_by(username=schema.username).first():
        raise ValidationError("Username already taken")
    
    # Création de l'utilisateur
    try:
        user = User(
            email=schema.email.lower(),
            username=schema.username,
            first_name=schema.first_name,
            last_name=schema.last_name,
        )
        user.set_password(schema.password)
        
        db.session.add(user)
        db.session.commit()
        
        # Générer le token avec le role
        access_token = create_access_token(user.id, user.role)
        
        logger.info(f'New user registered: {user.username}')
        
        user_data = UserResponseSchema.from_model(user)
        
        return jsonify({
            'access_token': access_token,
            'token_type': 'Bearer',
            'user': user_data.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error during registration: {e}', exc_info=True)
        raise DatabaseError("Failed to create user account")


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Connexion utilisateur.
    
    Request JSON:
        {
            "email": "string",
            "password": "string"
        }
    
    Returns:
        200: access_token
        401: Identifiants invalides
    """
    data = request.get_json()
    
    if not data:
        raise ValidationError("JSON data required")
    
    # Valider les données
    try:
        schema = UserLoginSchema(**data)
        schema.validate()
    except TypeError as e:
        raise ValidationError(f"Invalid request data: {str(e)}")
    
    # Rechercher l'utilisateur par email ou username
    user = None
    if schema.email:
        user = User.query.filter_by(email=schema.email.lower()).first()
    elif schema.username:
        user = User.query.filter_by(username=schema.username).first()
    
    if not user or not user.check_password(schema.password):
        raise AuthenticationError("Invalid credentials")
    
    if not user.is_active:
        raise AuthenticationError("Account has been deactivated")
    
    # Mettre à jour la dernière connexion
    try:
        user.update_last_login()
        db.session.commit()
    except Exception as e:
        logger.error(f'Error updating last login: {e}')
        # Non-bloquant, on continue
    
    # Générer les tokens avec le role
    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id)
    
    logger.info(f'User logged in: {user.username}')
    
    user_data = UserResponseSchema.from_model(user)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': 3600,  # 1 heure par défaut
        'user': user_data.to_dict()
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Rafraîchit un access token expiré avec un refresh token valide.
    
    Request JSON:
        {
            "refresh_token": "string"
        }
    
    Returns:
        200: Nouveau access_token
        401: Refresh token invalide ou expiré
    """
    data = request.get_json()
    
    if not data or not data.get('refresh_token'):
        raise ValidationError("refresh_token is required")
    
    # Décoder le refresh token
    payload = decode_refresh_token(data['refresh_token'])
    
    if not payload:
        raise AuthenticationError("Invalid or expired refresh token")
    
    # Récupérer l'utilisateur
    user = db.session.get(User, payload['user_id'])
    
    if not user or not user.is_active:
        raise AuthenticationError("User account not found or inactive")
    
    # Générer un nouveau access token
    new_access_token = create_access_token(user.id, user.role)
    
    logger.info(f'Token refreshed for user: {user.username}')
    
    return jsonify({
        'access_token': new_access_token,
        'token_type': 'Bearer',
        'expires_in': 3600
    }), 200


@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    """
    Vérifie si le token actuel est valide et retourne les infos.
    Utile pour vérifier la session côté frontend.
    
    Returns:
        200: Token valide avec infos utilisateur
        401: Token invalide
    """
    # Récupérer le token du header pour obtenir le temps restant
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.split(' ')[1] if ' ' in auth_header else ''
    remaining_time = get_token_remaining_time(token)
    
    user_data = UserResponseSchema.from_model(current_user)
    
    return jsonify({
        'valid': True,
        'user': user_data.to_dict(),
        'expires_in': remaining_time,
        'should_refresh': remaining_time and remaining_time < 300  # < 5 min
    }), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_me(current_user):
    """
    Recupere les informations de l'utilisateur connecte.
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Informations utilisateur
        401: Non authentifie
    """
    include_stats = request.args.get('stats', 'false').lower() == 'true'
    
    user_data = UserResponseSchema.from_model(current_user)
    response = {'user': user_data.to_dict()}
    
    if include_stats:
        response['stats'] = {
            'total_predictions': current_user.predictions.count(),
            'total_consultations': current_user.consultations.count(),
            'sports_predictions': current_user.predictions.filter_by(prediction_type='sports').count(),
            'finance_predictions': current_user.predictions.filter_by(prediction_type='finance').count(),
        }
    
    return jsonify(response), 200


@auth_bp.route('/me', methods=['PUT'])
@token_required
def update_me(current_user):
    """
    Met a jour le profil de l'utilisateur connecte.
    
    Request JSON:
        {
            "first_name": "string" (optionnel),
            "last_name": "string" (optionnel),
            "email": "string" (optionnel),
            "username": "string" (optionnel)
        }
    
    Returns:
        200: Profil mis a jour
        400: Erreur de validation
    """
    data = request.get_json() or {}
    
    # Mise a jour des champs autorises
    if 'first_name' in data:
        current_user.first_name = data['first_name']
    
    if 'last_name' in data:
        current_user.last_name = data['last_name']
    
    if 'email' in data:
        email = data['email'].lower().strip()
        if User.query.filter(User.email == email, User.id != current_user.id).first():
            raise ValidationError("Email already in use")
        current_user.email = email
    
    if 'username' in data:
        username = data['username'].strip()
        if User.query.filter(User.username == username, User.id != current_user.id).first():
            raise ValidationError("Username already taken")
        current_user.username = username
    
    try:
        db.session.commit()
        user_data = UserResponseSchema.from_model(current_user)
        return jsonify({
            'message': 'Profil mis a jour',
            'user': user_data.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error updating profile: {e}')
        raise DatabaseError("Failed to update profile")


@auth_bp.route('/password', methods=['PUT'])
@token_required
def change_password(current_user):
    """
    Change le mot de passe de l'utilisateur connecte.
    
    Request JSON:
        {
            "current_password": "string",
            "new_password": "string"
        }
    
    Returns:
        200: Mot de passe change
        400: Erreur de validation
        401: Mot de passe actuel incorrect
    """
    data = request.get_json()
    
    if not data:
        raise ValidationError("JSON data required")
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        raise ValidationError("Current and new password required")
    
    if not current_user.check_password(current_password):
        raise AuthenticationError("Current password is incorrect")
    
    if len(new_password) < 8:
        raise ValidationError("New password must be at least 8 characters")
    
    current_user.set_password(new_password)
    
    try:
        db.session.commit()
        logger.info(f'User {current_user.username} changed password')
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error changing password: {e}')
        raise DatabaseError("Failed to change password")
