"""
API Watchlist - Gestion des favoris utilisateur.
Endpoints pour ajouter/supprimer/lister les favoris.
"""

from flask import Blueprint, request, jsonify
import logging

from app.core.database import db
from app.core.errors import ValidationError, ResourceNotFoundError
from app.models.watchlist import Watchlist
from app.api.v1.auth import token_required

logger = logging.getLogger(__name__)

watchlist_bp = Blueprint('watchlist', __name__)

VALID_ITEM_TYPES = ['team', 'league', 'ticker', 'crypto']


@watchlist_bp.route('', methods=['GET'])
@token_required
def get_watchlist(current_user):
    """
    Récupère la watchlist de l'utilisateur.
    
    Query params:
        type: Filtrer par type ('team', 'league', 'ticker', 'crypto')
        alerts_only: Ne montrer que les items avec alertes activées
    
    Returns:
        Liste des favoris
    """
    user_id = current_user.id
    item_type = request.args.get('type')
    alerts_only = request.args.get('alerts_only', 'false').lower() == 'true'
    
    query = Watchlist.query.filter_by(user_id=user_id)
    
    if item_type and item_type in VALID_ITEM_TYPES:
        query = query.filter_by(item_type=item_type)
    
    if alerts_only:
        query = query.filter_by(alerts_enabled=True)
    
    items = query.order_by(Watchlist.created_at.desc()).all()
    
    # Grouper par type
    grouped = {t: [] for t in VALID_ITEM_TYPES}
    for item in items:
        if item.item_type in grouped:
            grouped[item.item_type].append(item.to_dict())
    
    return jsonify({
        'items': [item.to_dict() for item in items],
        'grouped': grouped,
        'count': len(items),
        'counts_by_type': {t: len(g) for t, g in grouped.items()}
    }), 200


@watchlist_bp.route('', methods=['POST'])
@token_required
def add_to_watchlist(current_user):
    """
    Ajoute un item à la watchlist.
    
    Request JSON:
        {
            "item_type": "team" | "league" | "ticker" | "crypto",
            "item_id": "string",
            "item_name": "string",
            "item_data": {} (optionnel),
            "notes": "string" (optionnel)
        }
    
    Returns:
        201: Item ajouté
        400: Données invalides
        409: Déjà dans la watchlist
    """
    user_id = current_user.id
    data = request.get_json()
    
    if not data:
        raise ValidationError("JSON data required")
    
    item_type = data.get('item_type')
    item_id = data.get('item_id')
    item_name = data.get('item_name')
    
    if not all([item_type, item_id, item_name]):
        raise ValidationError("item_type, item_id and item_name are required")
    
    if item_type not in VALID_ITEM_TYPES:
        raise ValidationError(f"Invalid item_type. Must be one of: {', '.join(VALID_ITEM_TYPES)}")
    
    # Vérifier si déjà présent
    existing = Watchlist.query.filter_by(
        user_id=user_id,
        item_type=item_type,
        item_id=str(item_id)
    ).first()
    
    if existing:
        return jsonify({
            'message': 'Item déjà dans la watchlist',
            'item': existing.to_dict()
        }), 409
    
    # Créer le nouvel item
    watchlist_item = Watchlist(
        user_id=user_id,
        item_type=item_type,
        item_id=str(item_id),
        item_name=item_name,
        item_data=data.get('item_data'),
        notes=data.get('notes'),
        alerts_enabled=data.get('alerts_enabled', False),
        alert_config=data.get('alert_config')
    )
    
    db.session.add(watchlist_item)
    db.session.commit()
    
    logger.info(f"User {user_id} added {item_type}:{item_id} to watchlist")
    
    return jsonify({
        'message': 'Ajouté à la watchlist',
        'item': watchlist_item.to_dict()
    }), 201


@watchlist_bp.route('/<int:item_id>', methods=['PUT'])
@token_required
def update_watchlist_item(current_user, item_id):
    """
    Met à jour un item de la watchlist.
    
    Request JSON:
        {
            "notes": "string",
            "alerts_enabled": boolean,
            "alert_config": {}
        }
    """
    user_id = current_user.id
    
    item = Watchlist.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        raise ResourceNotFoundError('Watchlist item', str(item_id))
    
    data = request.get_json() or {}
    
    if 'notes' in data:
        item.notes = data['notes']
    
    if 'alerts_enabled' in data:
        item.alerts_enabled = bool(data['alerts_enabled'])
    
    if 'alert_config' in data:
        item.alert_config = data['alert_config']
    
    if 'item_data' in data:
        item.item_data = data['item_data']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Watchlist mise à jour',
        'item': item.to_dict()
    }), 200


@watchlist_bp.route('/<int:item_id>', methods=['DELETE'])
@token_required
def remove_from_watchlist(current_user, item_id):
    """Supprime un item de la watchlist."""
    user_id = current_user.id
    
    item = Watchlist.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        raise ResourceNotFoundError('Watchlist item', str(item_id))
    
    item_info = f"{item.item_type}:{item.item_name}"
    db.session.delete(item)
    db.session.commit()
    
    logger.info(f"User {user_id} removed {item_info} from watchlist")
    
    return jsonify({
        'message': 'Supprimé de la watchlist'
    }), 200


@watchlist_bp.route('/check', methods=['GET'])
@token_required
def check_in_watchlist(current_user):
    """
    Vérifie si un item est dans la watchlist.
    
    Query params:
        type: Type d'item
        id: ID de l'item
    
    Returns:
        in_watchlist: boolean
        item: données si présent
    """
    user_id = current_user.id
    item_type = request.args.get('type')
    item_id = request.args.get('id')
    
    if not item_type or not item_id:
        raise ValidationError("type and id are required")
    
    item = Watchlist.query.filter_by(
        user_id=user_id,
        item_type=item_type,
        item_id=str(item_id)
    ).first()
    
    return jsonify({
        'in_watchlist': item is not None,
        'item': item.to_dict() if item else None
    }), 200


@watchlist_bp.route('/bulk', methods=['POST'])
@token_required
def bulk_add_watchlist(current_user):
    """
    Ajoute plusieurs items à la watchlist en une fois.
    
    Request JSON:
        {
            "items": [
                {"item_type": "...", "item_id": "...", "item_name": "..."},
                ...
            ]
        }
    """
    user_id = current_user.id
    data = request.get_json()
    
    if not data or 'items' not in data:
        raise ValidationError("items array required")
    
    items = data['items']
    added = []
    skipped = []
    
    for item_data in items[:50]:  # Max 50 items
        item_type = item_data.get('item_type')
        item_id = item_data.get('item_id')
        item_name = item_data.get('item_name')
        
        if not all([item_type, item_id, item_name]):
            continue
        
        if item_type not in VALID_ITEM_TYPES:
            continue
        
        # Vérifier si existe
        existing = Watchlist.query.filter_by(
            user_id=user_id,
            item_type=item_type,
            item_id=str(item_id)
        ).first()
        
        if existing:
            skipped.append({'item_id': item_id, 'reason': 'already_exists'})
            continue
        
        new_item = Watchlist(
            user_id=user_id,
            item_type=item_type,
            item_id=str(item_id),
            item_name=item_name,
            item_data=item_data.get('item_data')
        )
        db.session.add(new_item)
        added.append(new_item)
    
    db.session.commit()
    
    return jsonify({
        'message': f'{len(added)} items ajoutés',
        'added': [i.to_dict() for i in added],
        'skipped': skipped
    }), 201
