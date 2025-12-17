"""
Endpoints d'authentification.
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me
"""

import logging
from functools import wraps
from flask import Blueprint, request, jsonify

from app.core.database import db
from app.core.security import (
    create_access_token,
    decode_access_token,
    validate_email,
    validate_password_strength
)
from app.models.user import User

logger = logging.getLogger(__name__)

# Blueprint
auth_bp = Blueprint('auth', __name__)


def token_required(f):
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
                return jsonify({
                    'error': 'Format de token invalide',
                    'message': 'Utilisez: Bearer <token>'
                }), 401
        
        if not token:
            return jsonify({
                'error': 'Token manquant',
                'message': 'Veuillez vous authentifier.'
            }), 401
        
        # Decoder le token
        payload = decode_access_token(token)
        if not payload:
            return jsonify({
                'error': 'Token invalide ou expire',
                'message': 'Veuillez vous reconnecter.'
            }), 401
        
        # Recuperer l'utilisateur
        current_user = db.session.get(User, payload['user_id'])
        if not current_user or not current_user.is_active:
            return jsonify({
                'error': 'Utilisateur non trouve ou inactif',
                'message': 'Compte desactive ou supprime.'
            }), 401
        
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
        return jsonify({'error': 'Donnees JSON requises'}), 400
    
    # Validation des champs requis
    required_fields = ['email', 'username', 'password']
    missing_fields = [f for f in required_fields if not data.get(f)]
    
    if missing_fields:
        return jsonify({
            'error': 'Champs manquants',
            'details': {'missing_fields': missing_fields}
        }), 400
    
    email = data['email'].strip().lower()
    username = data['username'].strip()
    password = data['password']
    
    # Validation email
    if not validate_email(email):
        return jsonify({'error': 'Format d\'email invalide'}), 400
    
    # Validation username
    if len(username) < 3 or len(username) > 80:
        return jsonify({
            'error': 'Le nom d\'utilisateur doit contenir entre 3 et 80 caracteres'
        }), 400
    
    # Validation mot de passe
    is_valid, error_msg = validate_password_strength(password)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # Verification unicite email
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Cet email est deja utilise'}), 400
    
    # Verification unicite username
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Ce nom d\'utilisateur est deja pris'}), 400
    
    # Creation de l'utilisateur
    try:
        user = User(
            email=email,
            username=username,
            first_name=data.get('first_name', '').strip() or None,
            last_name=data.get('last_name', '').strip() or None,
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generer le token
        access_token = create_access_token(user.id)
        
        logger.info(f'Nouvel utilisateur inscrit: {user.username}')
        
        return jsonify({
            'access_token': access_token,
            'token_type': 'Bearer',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Erreur inscription: {e}')
        return jsonify({
            'error': 'Erreur lors de l\'inscription',
            'message': str(e)
        }), 500


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
        return jsonify({'error': 'Donnees JSON requises'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email et mot de passe requis'}), 400
    
    # Rechercher l'utilisateur
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({
            'error': 'Identifiants invalides',
            'message': 'Email ou mot de passe incorrect.'
        }), 401
    
    if not user.is_active:
        return jsonify({
            'error': 'Compte desactive',
            'message': 'Votre compte a ete desactive.'
        }), 401
    
    # Mettre a jour la derniere connexion
    user.update_last_login()
    db.session.commit()
    
    # Generer le token
    access_token = create_access_token(user.id)
    
    logger.info(f'Connexion reussie: {user.username}')
    
    return jsonify({
        'access_token': access_token,
        'token_type': 'Bearer',
        'user': user.to_dict()
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
    
    return jsonify({
        'user': current_user.to_dict(include_stats=include_stats)
    }), 200
