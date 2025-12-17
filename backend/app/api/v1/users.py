"""
Endpoints de gestion des utilisateurs (admin).
- GET /api/v1/users - Liste tous les utilisateurs (admin)
- GET /api/v1/users/<id> - Detail d'un utilisateur (admin)
- PUT /api/v1/users/<id> - Modifier un utilisateur (admin)
- DELETE /api/v1/users/<id> - Supprimer un utilisateur (admin)
- POST /api/v1/users/<id>/promote - Promouvoir en admin (admin)
- POST /api/v1/users/<id>/demote - Revoquer admin (admin)
"""

import logging
from flask import Blueprint, request, jsonify

from app.core.database import db
from app.core.errors import ValidationError, ResourceNotFoundError, AuthorizationError
from app.models.user import User, UserRole
from app.api.v1.auth import token_required, admin_required

logger = logging.getLogger(__name__)

# Blueprint
users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@token_required
@admin_required
def list_users(current_user):
    """
    Liste tous les utilisateurs (admin uniquement).
    
    Query params:
        - page: Numero de page (default: 1)
        - per_page: Nombre par page (default: 20, max: 100)
        - role: Filtrer par role (user/admin)
        - active: Filtrer par statut (true/false)
        - search: Recherche par email ou username
    
    Returns:
        200: Liste paginee des utilisateurs
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    role_filter = request.args.get('role')
    active_filter = request.args.get('active')
    search = request.args.get('search', '').strip()
    
    query = User.query
    
    # Filtres
    if role_filter and role_filter in UserRole.all_roles():
        query = query.filter_by(role=role_filter)
    
    if active_filter is not None:
        is_active = active_filter.lower() == 'true'
        query = query.filter_by(is_active=is_active)
    
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                User.email.ilike(search_pattern),
                User.username.ilike(search_pattern),
                User.first_name.ilike(search_pattern),
                User.last_name.ilike(search_pattern)
            )
        )
    
    # Pagination
    query = query.order_by(User.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    users = [u.to_dict(include_admin_info=True) for u in pagination.items]
    
    return jsonify({
        'users': users,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@token_required
@admin_required
def get_user(current_user, user_id):
    """
    Recupere les details d'un utilisateur (admin uniquement).
    
    Returns:
        200: Details de l'utilisateur
        404: Utilisateur non trouve
    """
    user = db.session.get(User, user_id)
    
    if not user:
        raise ResourceNotFoundError('User', str(user_id))
    
    return jsonify({
        'user': user.to_dict(include_stats=True, include_admin_info=True)
    }), 200


@users_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
@admin_required
def update_user(current_user, user_id):
    """
    Met a jour un utilisateur (admin uniquement).
    
    Request JSON:
        {
            "email": "string" (optionnel),
            "username": "string" (optionnel),
            "first_name": "string" (optionnel),
            "last_name": "string" (optionnel),
            "is_active": boolean (optionnel)
        }
    
    Returns:
        200: Utilisateur mis a jour
        400: Erreur de validation
        404: Utilisateur non trouve
    """
    user = db.session.get(User, user_id)
    
    if not user:
        raise ResourceNotFoundError('User', str(user_id))
    
    data = request.get_json() or {}
    
    # Mise a jour des champs
    if 'email' in data:
        email = data['email'].lower().strip()
        if User.query.filter(User.email == email, User.id != user_id).first():
            raise ValidationError('Email deja utilise')
        user.email = email
    
    if 'username' in data:
        username = data['username'].strip()
        if User.query.filter(User.username == username, User.id != user_id).first():
            raise ValidationError('Username deja utilise')
        user.username = username
    
    if 'first_name' in data:
        user.first_name = data['first_name']
    
    if 'last_name' in data:
        user.last_name = data['last_name']
    
    if 'is_active' in data:
        # Empecher un admin de se desactiver lui-meme
        if user.id == current_user.id and not data['is_active']:
            raise ValidationError('Vous ne pouvez pas vous desactiver vous-meme')
        user.is_active = data['is_active']
    
    try:
        db.session.commit()
        logger.info(f'Admin {current_user.username} updated user {user.username}')
        return jsonify({
            'message': 'Utilisateur mis a jour',
            'user': user.to_dict(include_admin_info=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error updating user: {e}')
        raise ValidationError('Erreur lors de la mise a jour')


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user, user_id):
    """
    Supprime un utilisateur (admin uniquement).
    
    Returns:
        200: Utilisateur supprime
        400: Impossible de se supprimer soi-meme
        404: Utilisateur non trouve
    """
    user = db.session.get(User, user_id)
    
    if not user:
        raise ResourceNotFoundError('User', str(user_id))
    
    if user.id == current_user.id:
        raise ValidationError('Vous ne pouvez pas supprimer votre propre compte')
    
    username = user.username
    
    try:
        db.session.delete(user)
        db.session.commit()
        logger.info(f'Admin {current_user.username} deleted user {username}')
        return jsonify({
            'message': f'Utilisateur {username} supprime'
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting user: {e}')
        raise ValidationError('Erreur lors de la suppression')


@users_bp.route('/<int:user_id>/promote', methods=['POST'])
@token_required
@admin_required
def promote_user(current_user, user_id):
    """
    Promouvoir un utilisateur en admin.
    
    Returns:
        200: Utilisateur promu
        404: Utilisateur non trouve
    """
    user = db.session.get(User, user_id)
    
    if not user:
        raise ResourceNotFoundError('User', str(user_id))
    
    if user.is_admin:
        return jsonify({
            'message': 'Utilisateur deja admin',
            'user': user.to_dict()
        }), 200
    
    user.make_admin()
    
    try:
        db.session.commit()
        logger.info(f'Admin {current_user.username} promoted {user.username} to admin')
        return jsonify({
            'message': f'{user.username} est maintenant admin',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error promoting user: {e}')
        raise ValidationError('Erreur lors de la promotion')


@users_bp.route('/<int:user_id>/demote', methods=['POST'])
@token_required
@admin_required
def demote_user(current_user, user_id):
    """
    Revoquer les droits admin d'un utilisateur.
    
    Returns:
        200: Droits revoques
        400: Impossible de se revoquer soi-meme
        404: Utilisateur non trouve
    """
    user = db.session.get(User, user_id)
    
    if not user:
        raise ResourceNotFoundError('User', str(user_id))
    
    if user.id == current_user.id:
        raise ValidationError('Vous ne pouvez pas revoquer vos propres droits admin')
    
    if not user.is_admin:
        return jsonify({
            'message': 'Utilisateur n\'est pas admin',
            'user': user.to_dict()
        }), 200
    
    user.revoke_admin()
    
    try:
        db.session.commit()
        logger.info(f'Admin {current_user.username} demoted {user.username}')
        return jsonify({
            'message': f'{user.username} n\'est plus admin',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error demoting user: {e}')
        raise ValidationError('Erreur lors de la revocation')


@users_bp.route('/stats', methods=['GET'])
@token_required
@admin_required
def get_stats(current_user):
    """
    Statistiques globales des utilisateurs (admin uniquement).
    
    Returns:
        200: Statistiques
    """
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(role=UserRole.ADMIN).count()
    
    return jsonify({
        'stats': {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'admin_users': admin_users,
            'regular_users': total_users - admin_users
        }
    }), 200
