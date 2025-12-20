"""
API Live - Endpoints temps réel (polling + SSE).

Fournit:
- GET /api/v1/live/config - Configuration polling
- GET /api/v1/live/status - Status cache et scheduler
- GET /api/v1/live/stream - SSE pour updates temps réel
- POST /api/v1/live/subscribe - Abonnement aux updates
"""

import uuid
import time
import json
import logging
from flask import Blueprint, jsonify, request, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.core.live import (
    live_cache, 
    background_scheduler, 
    sse_manager,
    RESOURCE_TTL,
    POLLING_INTERVALS,
    ResourceType,
)
from app.core.config import Config

logger = logging.getLogger(__name__)

live_bp = Blueprint('live', __name__)


@live_bp.route('/config', methods=['GET'])
def get_live_config():
    """
    Retourne la configuration live pour le frontend.
    Permet au client de configurer son polling intelligemment.
    """
    return jsonify({
        "enabled": Config.LIVE_MODE_ENABLED,
        "polling_intervals": POLLING_INTERVALS,
        "resource_ttl": {rt.value: ttl for rt, ttl in RESOURCE_TTL.items()},
        "recommended": {
            "finance": {
                "ticker_interval": Config.LIVE_POLL_FINANCE_NORMAL,
                "list_interval": Config.LIVE_TTL_FINANCE_LIST,
            },
            "sports": {
                "match_interval": Config.LIVE_POLL_SPORTS_NORMAL,
                "list_interval": Config.LIVE_TTL_SPORTS_LIST,
            },
        },
        "thresholds": {
            "price_change_percent": Config.AI_RECALC_PRICE_THRESHOLD,
            "odds_change_percent": Config.AI_RECALC_ODDS_THRESHOLD,
        }
    })


@live_bp.route('/status', methods=['GET'])
@jwt_required()
def get_live_status():
    """
    Retourne le status du système live (cache, scheduler, SSE).
    Réservé aux utilisateurs authentifiés.
    """
    return jsonify({
        "cache": live_cache.get_stats(),
        "scheduler": background_scheduler.get_status(),
        "sse": sse_manager.get_stats(),
        "timestamp": time.time(),
    })


@live_bp.route('/stream', methods=['GET'])
@jwt_required()
def sse_stream():
    """
    Endpoint SSE pour recevoir les updates en temps réel.
    
    Query params:
        - channels: Canaux à écouter (comma-separated)
                   Ex: finance,sports,dashboard
    """
    user_id = get_jwt_identity()
    client_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
    
    # Récupérer les canaux demandés
    channels = request.args.get('channels', 'global').split(',')
    channels = [c.strip() for c in channels if c.strip()]
    
    # Enregistrer le client
    sse_manager.register_client(client_id, channels)
    
    def generate():
        """Générateur SSE."""
        try:
            # Envoyer un message de connexion
            yield f"event: connected\ndata: {json.dumps({'client_id': client_id, 'channels': channels})}\n\n"
            
            queue = sse_manager.get_client_queue(client_id)
            if not queue:
                return
            
            # Heartbeat et messages
            last_heartbeat = time.time()
            
            while True:
                # Vérifier si messages disponibles
                try:
                    from queue import Empty
                    message = queue.get(timeout=1)
                    yield f"event: {message['event']}\ndata: {json.dumps(message['data'])}\n\n"
                except Empty:
                    pass
                
                # Heartbeat toutes les 30s
                if time.time() - last_heartbeat > 30:
                    yield f"event: heartbeat\ndata: {json.dumps({'timestamp': time.time()})}\n\n"
                    last_heartbeat = time.time()
                    
        except GeneratorExit:
            pass
        finally:
            sse_manager.unregister_client(client_id)
    
    response = Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',  # Nginx
        }
    )
    return response


@live_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe_updates():
    """
    Configure les abonnements pour les updates.
    Le frontend indique quelles ressources surveiller.
    
    Body:
    {
        "subscriptions": [
            {"type": "finance:ticker", "id": "AAPL"},
            {"type": "sports:match", "id": "mock_1"},
        ]
    }
    """
    data = request.get_json() or {}
    subscriptions = data.get('subscriptions', [])
    
    # Valider les abonnements
    valid_types = [rt.value for rt in ResourceType]
    validated = []
    
    for sub in subscriptions:
        if sub.get('type') in valid_types:
            validated.append({
                "type": sub['type'],
                "id": sub.get('id', '*'),
                "interval": RESOURCE_TTL.get(
                    ResourceType(sub['type']), 
                    60
                )
            })
    
    return jsonify({
        "subscriptions": validated,
        "message": f"Abonné à {len(validated)} ressources"
    })


@live_bp.route('/poll/<resource_type>/<identifier>', methods=['GET'])
@jwt_required()
def poll_resource(resource_type: str, identifier: str):
    """
    Endpoint de polling intelligent.
    Retourne 304 si données inchangées (basé sur If-None-Match header).
    
    Headers:
        If-None-Match: <data_version> - Version actuelle du client
    
    Returns:
        200 + data si nouvelles données
        304 Not Modified si inchangé
    """
    # Valider le type de ressource
    try:
        rt = ResourceType(resource_type)
    except ValueError:
        return jsonify({"error": f"Type de ressource invalide: {resource_type}"}), 400
    
    # Vérifier la version du client
    client_version = request.headers.get('If-None-Match', '').strip('"')
    
    # Chercher dans le cache
    cached = live_cache.get(rt, identifier, check_version=client_version)
    
    if cached and client_version and cached.data_version == client_version:
        # Données inchangées
        return '', 304
    
    if cached:
        # Retourner les données cachées
        response = jsonify({
            "data": cached.value,
            "_live": cached.to_metadata(),
        })
        response.headers['ETag'] = f'"{cached.data_version}"'
        return response
    
    # Pas de cache - le client doit appeler l'endpoint principal
    return jsonify({
        "error": "Resource not in cache",
        "hint": "Call the main endpoint first"
    }), 404


@live_bp.route('/invalidate', methods=['POST'])
@jwt_required()
def invalidate_cache():
    """
    Invalide des entrées de cache (admin seulement ou propre user).
    
    Body:
    {
        "resource_type": "finance:ticker",
        "identifier": "AAPL"  // Optionnel, si absent invalide tout le type
    }
    """
    data = request.get_json() or {}
    resource_type_str = data.get('resource_type')
    identifier = data.get('identifier')
    
    if not resource_type_str:
        return jsonify({"error": "resource_type requis"}), 400
    
    try:
        rt = ResourceType(resource_type_str)
    except ValueError:
        return jsonify({"error": f"Type invalide: {resource_type_str}"}), 400
    
    if identifier:
        success = live_cache.invalidate(rt, identifier)
        return jsonify({
            "invalidated": success,
            "resource": f"{resource_type_str}:{identifier}"
        })
    else:
        count = live_cache.invalidate_pattern(rt)
        return jsonify({
            "invalidated_count": count,
            "resource_type": resource_type_str
        })


# ============================================
# Background Jobs pour updates
# ============================================

def setup_background_jobs():
    """Configure les jobs de background pour les updates."""
    from app.services.finance_api_service import finance_service
    from app.services.sports_api_service import sports_service
    
    def update_finance_watchlist():
        """Met à jour les données des tickers populaires."""
        try:
            popular = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
            for ticker in popular:
                try:
                    data = finance_service.get_stock_data(ticker)
                    if data:
                        live_cache.set(
                            ResourceType.FINANCE_TICKER,
                            ticker.lower(),
                            data,
                            ttl=Config.LIVE_TTL_FINANCE_TICKER
                        )
                        # Notifier les clients SSE
                        sse_manager.broadcast(
                            "finance:update",
                            {"ticker": ticker, "data": data},
                            channel="finance"
                        )
                except Exception as e:
                    logger.error(f"Update finance {ticker}: {e}")
        except Exception as e:
            logger.error(f"Update finance watchlist error: {e}")
    
    def update_sports_matches():
        """Met à jour les matchs en cours."""
        try:
            matches = sports_service.get_matches(limit=10)
            if matches:
                live_cache.set(
                    ResourceType.SPORTS_LIST,
                    "upcoming",
                    matches,
                    ttl=Config.LIVE_TTL_SPORTS_LIST
                )
                # Notifier les clients SSE
                sse_manager.broadcast(
                    "sports:update",
                    {"type": "matches", "count": len(matches.get('matches', []))},
                    channel="sports"
                )
        except Exception as e:
            logger.error(f"Update sports matches error: {e}")
    
    # Ajouter les jobs
    background_scheduler.add_job(
        "finance_watchlist",
        update_finance_watchlist,
        Config.SCHEDULER_FINANCE_WATCHLIST
    )
    
    background_scheduler.add_job(
        "sports_matches",
        update_sports_matches,
        Config.SCHEDULER_SPORTS_MATCHES
    )
    
    logger.info("Background jobs configurés")


def start_scheduler():
    """Démarre le scheduler de background."""
    if Config.LIVE_MODE_ENABLED:
        setup_background_jobs()
        background_scheduler.start()
        logger.info("Live scheduler démarré")
