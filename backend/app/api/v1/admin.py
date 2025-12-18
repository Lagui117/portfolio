"""
API Administration - Gestion utilisateurs et supervision système.
Endpoints réservés aux administrateurs.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import logging

from app.core.database import db
from app.models.user import User, UserRole
from app.models.prediction import Prediction
from app.models.consultation import Consultation
from app.api.v1.auth import token_required, admin_required

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)


# ============================================
# GESTION DES UTILISATEURS
# ============================================

@admin_bp.route('/users', methods=['GET'])
@token_required
@admin_required
def list_users(current_user):
    """
    Liste tous les utilisateurs avec pagination.
    
    Query params:
        page (int): Page courante (default 1)
        per_page (int): Éléments par page (default 20, max 100)
        role (str): Filtrer par rôle ('user', 'admin')
        status (str): Filtrer par statut ('active', 'inactive')
        search (str): Recherche par email ou username
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        role_filter = request.args.get('role')
        status_filter = request.args.get('status')
        search = request.args.get('search', '').strip()
        
        query = User.query
        
        # Filtres
        if role_filter in UserRole.all_roles():
            query = query.filter_by(role=role_filter)
        
        if status_filter == 'active':
            query = query.filter_by(is_active=True)
        elif status_filter == 'inactive':
            query = query.filter_by(is_active=False)
        
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    User.email.ilike(search_pattern),
                    User.username.ilike(search_pattern)
                )
            )
        
        # Pagination
        query = query.order_by(User.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        users = [user.to_dict(include_stats=True) for user in pagination.items]
        
        return jsonify({
            'users': users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur liste utilisateurs: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
@admin_required
def get_user(current_user, user_id):
    """Récupère les détails d'un utilisateur."""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        return jsonify({
            'user': user.to_dict(include_stats=True)
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur récupération utilisateur: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
@admin_required
def update_user(current_user, user_id):
    """
    Met à jour un utilisateur (admin only).
    
    Body:
        role (str): Nouveau rôle
        is_active (bool): Statut actif
        first_name (str): Prénom
        last_name (str): Nom
    """
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        data = request.get_json()
        
        # Mise à jour du rôle
        if 'role' in data and data['role'] in UserRole.all_roles():
            # Empêcher un admin de se rétrograder lui-même
            if user.id == current_user.id and data['role'] != UserRole.ADMIN:
                return jsonify({
                    'error': 'Vous ne pouvez pas révoquer vos propres droits admin'
                }), 400
            user.role = data['role']
        
        # Mise à jour du statut
        if 'is_active' in data:
            # Empêcher un admin de se désactiver lui-même
            if user.id == current_user.id and not data['is_active']:
                return jsonify({
                    'error': 'Vous ne pouvez pas désactiver votre propre compte'
                }), 400
            user.is_active = data['is_active']
        
        # Autres champs
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        db.session.commit()
        
        logger.info(f"Admin {current_user.username} a modifié l'utilisateur {user.username}")
        
        return jsonify({
            'message': 'Utilisateur mis à jour',
            'user': user.to_dict(include_stats=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur mise à jour utilisateur: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user, user_id):
    """Supprime un utilisateur (soft delete via is_active=False ou hard delete)."""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Empêcher un admin de se supprimer lui-même
        if user.id == current_user.id:
            return jsonify({
                'error': 'Vous ne pouvez pas supprimer votre propre compte'
            }), 400
        
        hard_delete = request.args.get('hard', 'false').lower() == 'true'
        
        if hard_delete:
            username = user.username
            db.session.delete(user)
            db.session.commit()
            logger.info(f"Admin {current_user.username} a supprimé définitivement {username}")
            return jsonify({'message': f'Utilisateur {username} supprimé définitivement'}), 200
        else:
            user.is_active = False
            db.session.commit()
            logger.info(f"Admin {current_user.username} a désactivé {user.username}")
            return jsonify({
                'message': f'Utilisateur {user.username} désactivé',
                'user': user.to_dict()
            }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur suppression utilisateur: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500


# ============================================
# STATISTIQUES SYSTÈME
# ============================================

@admin_bp.route('/stats', methods=['GET'])
@token_required
@admin_required
def get_system_stats(current_user):
    """Statistiques globales du système."""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_count = User.query.filter_by(role=UserRole.ADMIN).count()
        
        total_predictions = Prediction.query.count()
        sports_predictions = Prediction.query.filter_by(prediction_type='sports').count()
        finance_predictions = Prediction.query.filter_by(prediction_type='finance').count()
        
        total_consultations = Consultation.query.count()
        
        # Utilisateurs récents (7 derniers jours)
        from datetime import timedelta
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        new_users_week = User.query.filter(User.created_at >= week_ago).count()
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'inactive': total_users - active_users,
                'admins': admin_count,
                'new_this_week': new_users_week
            },
            'predictions': {
                'total': total_predictions,
                'sports': sports_predictions,
                'finance': finance_predictions
            },
            'consultations': {
                'total': total_consultations
            },
            'generated_at': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur stats système: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500


# ============================================
# LOGS D'ACTIVITÉ
# ============================================

@admin_bp.route('/activity', methods=['GET'])
@token_required
@admin_required
def get_activity_logs(current_user):
    """
    Récupère les logs d'activité récents.
    
    Query params:
        limit (int): Nombre de logs (default 50, max 200)
        type (str): Type d'activité ('prediction', 'consultation', 'login')
    """
    try:
        limit = min(request.args.get('limit', 50, type=int), 200)
        activity_type = request.args.get('type')
        
        activities = []
        
        # Dernières prédictions
        if not activity_type or activity_type == 'prediction':
            predictions = Prediction.query.order_by(
                Prediction.created_at.desc()
            ).limit(limit).all()
            
            for pred in predictions:
                user = db.session.get(User, pred.user_id)
                details = 'N/A'
                if pred.input_data:
                    details = pred.input_data.get('symbol') or pred.input_data.get('match_id', 'N/A')
                elif pred.ticker:
                    details = pred.ticker
                elif pred.external_match_id:
                    details = pred.external_match_id
                activities.append({
                    'type': 'prediction',
                    'subtype': pred.prediction_type,
                    'user': user.username if user else 'Unknown',
                    'user_id': pred.user_id,
                    'details': details,
                    'timestamp': pred.created_at.isoformat() if pred.created_at else None
                })
        
        # Dernières consultations
        if not activity_type or activity_type == 'consultation':
            consultations = Consultation.query.order_by(
                Consultation.created_at.desc()
            ).limit(limit).all()
            
            for cons in consultations:
                user = db.session.get(User, cons.user_id)
                activities.append({
                    'type': 'consultation',
                    'subtype': cons.consultation_type,
                    'user': user.username if user else 'Unknown',
                    'user_id': cons.user_id,
                    'details': cons.query_params.get('query', 'N/A') if cons.query_params else 'N/A',
                    'timestamp': cons.created_at.isoformat() if cons.created_at else None
                })
        
        # Trier par timestamp
        activities.sort(key=lambda x: x['timestamp'] or '', reverse=True)
        activities = activities[:limit]
        
        return jsonify({
            'activities': activities,
            'count': len(activities)
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur logs activité: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500


# ============================================
# ACTIONS RAPIDES
# ============================================

@admin_bp.route('/users/<int:user_id>/promote', methods=['POST'])
@token_required
@admin_required
def promote_user(current_user, user_id):
    """Promouvoir un utilisateur en administrateur."""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if user.is_admin:
            return jsonify({'message': 'Utilisateur déjà administrateur'}), 200
        
        user.make_admin()
        db.session.commit()
        
        logger.info(f"Admin {current_user.username} a promu {user.username} en admin")
        
        return jsonify({
            'message': f'{user.username} est maintenant administrateur',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur promotion utilisateur: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500


@admin_bp.route('/users/<int:user_id>/demote', methods=['POST'])
@token_required
@admin_required
def demote_user(current_user, user_id):
    """Rétrograder un administrateur en utilisateur standard."""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if user.id == current_user.id:
            return jsonify({
                'error': 'Vous ne pouvez pas révoquer vos propres droits'
            }), 400
        
        if not user.is_admin:
            return jsonify({'message': 'Utilisateur déjà standard'}), 200
        
        user.revoke_admin()
        db.session.commit()
        
        logger.info(f"Admin {current_user.username} a rétrogradé {user.username}")
        
        return jsonify({
            'message': f'{user.username} est maintenant utilisateur standard',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur rétrogradation utilisateur: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500
