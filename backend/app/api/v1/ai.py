"""
API AI - Endpoint principal pour l'intelligence artificielle PredictWise.

Fournit:
- POST /ai/chat: Chat conversationnel avec contexte
- POST /ai/analyze: Analyse ponctuelle avec données
- GET /ai/health: Vérification du service IA
"""

from flask import Blueprint, request, jsonify
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.api.v1.auth import token_required
from app.services.chat_service import chat_service

logger = logging.getLogger(__name__)

ai_bp = Blueprint('ai', __name__)


# ============================================
# HEALTH CHECK
# ============================================

@ai_bp.route('/health', methods=['GET'])
def health_check():
    """
    Vérifie la santé du service IA.
    
    Returns:
        JSON avec le status du service
    """
    openai_key_present = bool(os.getenv('OPENAI_API_KEY'))
    
    status = {
        'service': 'ai',
        'status': 'healthy' if chat_service.client else 'degraded',
        'openai_configured': openai_key_present,
        'model': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        'timestamp': datetime.utcnow().isoformat(),
        'features': {
            'chat': chat_service.client is not None,
            'fallback': True,  # Toujours disponible
        }
    }
    
    return jsonify(status), 200


# ============================================
# CHAT ENDPOINT
# ============================================

@ai_bp.route('/chat', methods=['POST'])
@token_required
def chat(current_user):
    """
    Endpoint principal de chat avec l'IA.
    
    Body:
        message (str): Message de l'utilisateur (required)
        context (dict, optional): Contexte additionnel
            - current_analysis: Analyse en cours (type, symbol, teams, prediction, confidence)
            - page: Page actuelle de l'utilisateur
            - recent_queries: Dernières requêtes
        conversation_id (str, optional): ID de conversation pour continuité
    
    Returns:
        {
            "answer": "Réponse de l'IA",
            "confidence": 0.85,
            "used_context": true,
            "citations": [...],
            "conversation_id": "uuid",
            "metadata": {
                "model": "gpt-4o-mini",
                "tokens_used": 150,
                "response_time_ms": 450
            }
        }
    
    Errors:
        400: Message manquant ou invalide
        500: Erreur de traitement
    """
    start_time = datetime.utcnow()
    
    try:
        data = request.get_json()
        
        # Validation
        if not data:
            return jsonify({
                'error': {
                    'type': 'validation_error',
                    'message': 'Corps de requête JSON requis'
                }
            }), 400
        
        message = data.get('message', '').strip()
        if not message:
            return jsonify({
                'error': {
                    'type': 'validation_error',
                    'message': 'Message requis et non vide'
                }
            }), 400
        
        if len(message) > 2000:
            return jsonify({
                'error': {
                    'type': 'validation_error',
                    'message': 'Message trop long (max 2000 caractères)'
                }
            }), 400
        
        # Extraire les paramètres optionnels
        context = data.get('context', {})
        conversation_id = data.get('conversation_id')
        
        # Appeler le service de chat
        result = chat_service.process_message(
            user_id=str(current_user.id),
            message=message,
            context=context,
            conversation_id=conversation_id
        )
        
        # Calculer le temps de réponse
        response_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Construire la réponse formatée
        response = {
            'answer': result['response']['content'],
            'confidence': _calculate_confidence(result['response']['content'], context),
            'used_context': bool(context and context.get('current_analysis')),
            'citations': _extract_citations(result['response']['content']),
            'conversation_id': result['conversation_id'],
            'metadata': {
                'model': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                'response_time_ms': round(response_time_ms, 2),
                'fallback_mode': chat_service.client is None,
                'message_count': result.get('message_count', 1)
            }
        }
        
        logger.info(
            f"AI Chat | user={current_user.id} | "
            f"context={bool(context)} | "
            f"time_ms={response_time_ms:.2f}"
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Erreur AI Chat: {e}", exc_info=True)
        return jsonify({
            'error': {
                'type': 'internal_error',
                'message': 'Erreur de traitement de la requête'
            },
            'answer': "Je suis momentanément indisponible. Veuillez réessayer.",
            'confidence': 0,
            'used_context': False,
            'citations': [],
            'metadata': {
                'fallback_mode': True,
                'error': str(e) if os.getenv('FLASK_DEBUG') else None
            }
        }), 500


# ============================================
# ANALYZE ENDPOINT (one-shot analysis)
# ============================================

@ai_bp.route('/analyze', methods=['POST'])
@token_required
def analyze(current_user):
    """
    Analyse ponctuelle de données (sans historique de conversation).
    
    Body:
        type (str): Type d'analyse ('sports' ou 'finance')
        data (dict): Données à analyser (format normalisé)
        question (str, optional): Question spécifique
    
    Returns:
        Analyse structurée avec recommandations
    """
    try:
        data = request.get_json()
        
        if not data or 'type' not in data or 'data' not in data:
            return jsonify({
                'error': {
                    'type': 'validation_error',
                    'message': 'Type et data requis'
                }
            }), 400
        
        analysis_type = data['type']
        analysis_data = data['data']
        question = data.get('question', f"Analyse ces données {analysis_type}")
        
        # Construire le contexte pour l'analyse
        context = {
            'current_analysis': {
                'type': analysis_type,
                **_extract_analysis_context(analysis_type, analysis_data)
            },
            'page': f'{analysis_type}_dashboard'
        }
        
        # Appeler le chat service en mode one-shot
        result = chat_service.process_message(
            user_id=str(current_user.id),
            message=question,
            context=context,
            conversation_id=None  # Pas de continuité
        )
        
        return jsonify({
            'analysis': result['response']['content'],
            'type': analysis_type,
            'data_summary': _summarize_data(analysis_type, analysis_data),
            'confidence': _calculate_confidence(result['response']['content'], context),
            'metadata': {
                'model': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                'fallback_mode': chat_service.client is None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur AI Analyze: {e}", exc_info=True)
        return jsonify({
            'error': {
                'type': 'internal_error',
                'message': 'Erreur d\'analyse'
            }
        }), 500


# ============================================
# HELPER FUNCTIONS
# ============================================

def _calculate_confidence(response: str, context: Dict[str, Any]) -> float:
    """
    Calcule un score de confiance basé sur la réponse.
    
    Heuristique basée sur:
    - Longueur de la réponse
    - Présence de contexte
    - Indicateurs de certitude dans le texte
    """
    if not response:
        return 0.0
    
    base_confidence = 0.5
    
    # Bonus si contexte fourni
    if context and context.get('current_analysis'):
        base_confidence += 0.2
    
    # Ajustement basé sur la longueur
    if len(response) > 200:
        base_confidence += 0.1
    
    # Pénalité si réponse de fallback détectée
    fallback_indicators = [
        "service IA complet",
        "momentanément indisponible",
        "mode dégradé"
    ]
    if any(ind in response.lower() for ind in fallback_indicators):
        base_confidence -= 0.3
    
    return min(max(base_confidence, 0.0), 1.0)


def _extract_citations(response: str) -> list:
    """
    Extrait les citations/références de la réponse.
    
    Pour l'instant retourne une liste vide car GPT ne cite pas de sources.
    Pourrait être étendu avec RAG/embeddings.
    """
    # TODO: Implémenter l'extraction de citations avec RAG
    return []


def _extract_analysis_context(
    analysis_type: str, 
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """Extrait le contexte pertinent des données d'analyse."""
    context = {}
    
    if analysis_type == 'sports':
        if 'home_team' in data:
            context['teams'] = f"{data['home_team'].get('name', 'Home')} vs {data.get('away_team', {}).get('name', 'Away')}"
        if 'prediction' in data:
            context['prediction'] = data['prediction']
        if 'confidence' in data:
            context['confidence'] = data['confidence']
            
    elif analysis_type == 'finance':
        if 'symbol' in data:
            context['symbol'] = data['symbol']
        if 'current_price' in data:
            context['price'] = data['current_price']
        if 'change_percent' in data:
            context['change'] = f"{data['change_percent']}%"
        if 'indicators' in data:
            ind = data['indicators']
            if 'rsi_14' in ind:
                context['rsi'] = ind['rsi_14']
    
    return context


def _summarize_data(analysis_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Crée un résumé des données analysées."""
    if analysis_type == 'sports':
        return {
            'match': f"{data.get('home_team', {}).get('name', '?')} vs {data.get('away_team', {}).get('name', '?')}",
            'competition': data.get('competition', 'Unknown'),
            'status': data.get('status', 'unknown')
        }
    elif analysis_type == 'finance':
        return {
            'symbol': data.get('symbol', 'N/A'),
            'price': data.get('current_price', 0),
            'change': f"{data.get('change_percent', 0):.2f}%",
            'sector': data.get('sector', 'Unknown')
        }
    return {}


# ============================================
# LEGACY ENDPOINT (backward compatibility)
# ============================================

@ai_bp.route('/gpt/analyze', methods=['POST'])
@token_required
def legacy_gpt_analyze(current_user):
    """
    Endpoint legacy pour compatibilité avec l'ancien code.
    Réimplémente la logique d'analyze pour éviter la double injection.
    """
    try:
        data = request.get_json()
        
        if not data or 'type' not in data or 'data' not in data:
            return jsonify({
                'error': {
                    'type': 'validation_error',
                    'message': 'Type et data requis'
                }
            }), 400
        
        analysis_type = data['type']
        analysis_data = data['data']
        question = data.get('question', f"Analyse ces données {analysis_type}")
        
        # Construire le contexte pour l'analyse
        context = {
            'current_analysis': {
                'type': analysis_type,
                **_extract_analysis_context(analysis_type, analysis_data)
            },
            'page': f'{analysis_type}_dashboard'
        }
        
        # Appeler le chat service en mode one-shot
        result = chat_service.process_message(
            user_id=str(current_user.id),
            message=question,
            context=context,
            conversation_id=None
        )
        
        return jsonify({
            'analysis': result['response']['content'],
            'type': analysis_type,
            'data_summary': _summarize_data(analysis_type, analysis_data),
            'confidence': _calculate_confidence(result['response']['content'], context),
            'metadata': {
                'model': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                'fallback_mode': chat_service.client is None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur Legacy GPT Analyze: {e}", exc_info=True)
        return jsonify({
            'error': {
                'type': 'internal_error',
                'message': 'Erreur d\'analyse'
            }
        }), 500


# ============================================
# LIVE AI ANALYZE (avec versioning et auto-update)
# ============================================

@ai_bp.route('/analyze/live', methods=['POST'])
@token_required
def analyze_live(current_user):
    """
    Analyse IA avec support live (versioning + recalcul intelligent).
    
    Ne recalcule l'analyse que si:
    - data_version différent (données ont changé)
    - ET variation significative (seuil dépassé)
    
    Body:
        domain (str): 'sports' ou 'finance'
        entity_id (str): Identifiant (ticker, match_id)
        data_version (str, optional): Version des données côté client
        data (dict): Données à analyser
        force_refresh (bool, optional): Force le recalcul
    
    Returns:
        {
            "analysis": {...},
            "data_version": "abc123",
            "updated_at": "2025-01-01T00:00:00",
            "recalculated": true/false,
            "reason": "price_change" | "cached" | "forced"
        }
    """
    from app.core.live import live_cache, ResourceType, make_live_response
    from app.core.config import Config
    import hashlib
    import json
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': {'message': 'Body requis'}}), 400
        
        domain = data.get('domain', data.get('type'))  # Support les 2 formats
        entity_id = data.get('entity_id', '')
        client_version = data.get('data_version')
        analysis_data = data.get('data', {})
        force_refresh = data.get('force_refresh', False)
        
        if not domain:
            return jsonify({'error': {'message': 'domain requis'}}), 400
        
        # Générer la version des données actuelles
        current_version = hashlib.md5(
            json.dumps(analysis_data, sort_keys=True, default=str).encode()
        ).hexdigest()[:12]
        
        # Clé de cache pour cette analyse
        cache_key = f"{domain}:{entity_id}"
        
        # Vérifier le cache d'analyse IA
        cached_analysis = live_cache.get(
            ResourceType.AI_ANALYSIS, 
            cache_key,
            check_version=client_version
        )
        
        # Décider si on recalcule
        should_recalculate = force_refresh
        recalc_reason = "forced" if force_refresh else None
        
        if not should_recalculate and cached_analysis:
            # Vérifier si les données ont changé significativement
            if client_version != current_version:
                # Calculer le seuil de variation
                variation = _calculate_variation(domain, analysis_data, cached_analysis.value.get('_source_data', {}))
                
                threshold = (
                    Config.AI_RECALC_PRICE_THRESHOLD if domain == 'finance'
                    else Config.AI_RECALC_ODDS_THRESHOLD
                )
                
                if variation > threshold:
                    should_recalculate = True
                    recalc_reason = f"{domain}_change"
        elif not cached_analysis:
            should_recalculate = True
            recalc_reason = "no_cache"
        
        # Retourner le cache si pas de recalcul nécessaire
        if not should_recalculate and cached_analysis:
            response = {
                **cached_analysis.value,
                'recalculated': False,
                'reason': 'cached',
                '_live': cached_analysis.to_metadata(),
            }
            return jsonify(response), 200
        
        # Recalculer l'analyse
        question = data.get('question', f"Analyse ces données {domain}")
        context = {
            'current_analysis': {
                'type': domain,
                **_extract_analysis_context(domain, analysis_data)
            },
            'page': f'{domain}_dashboard'
        }
        
        result = chat_service.process_message(
            user_id=str(current_user.id),
            message=question,
            context=context,
            conversation_id=None
        )
        
        analysis_result = {
            'analysis': result['response']['content'],
            'type': domain,
            'entity_id': entity_id,
            'data_summary': _summarize_data(domain, analysis_data),
            'confidence': _calculate_confidence(result['response']['content'], context),
            '_source_data': analysis_data,  # Pour comparaison future
            'metadata': {
                'model': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                'fallback_mode': chat_service.client is None
            }
        }
        
        # Mettre en cache
        cached = live_cache.set(
            ResourceType.AI_ANALYSIS,
            cache_key,
            analysis_result,
            ttl=Config.LIVE_TTL_AI_ANALYSIS,
            force_version=current_version
        )
        
        response = {
            **analysis_result,
            'recalculated': True,
            'reason': recalc_reason,
            '_live': cached.to_metadata(),
        }
        
        # Supprimer _source_data de la réponse (usage interne)
        response.pop('_source_data', None)
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Erreur AI Analyze Live: {e}", exc_info=True)
        return jsonify({
            'error': {
                'type': 'internal_error',
                'message': 'Erreur d\'analyse live'
            }
        }), 500


def _calculate_variation(domain: str, new_data: dict, old_data: dict) -> float:
    """
    Calcule la variation entre anciennes et nouvelles données.
    Retourne un pourcentage (0.0 = identique, 1.0 = 100% différent).
    """
    try:
        if domain == 'finance':
            # Variation du prix
            old_price = old_data.get('current_price', old_data.get('price', 0))
            new_price = new_data.get('current_price', new_data.get('price', 0))
            
            if old_price and new_price:
                return abs((new_price - old_price) / old_price) * 100
            return 100.0  # Force recalcul si pas de prix
        
        elif domain == 'sports':
            # Variation des cotes
            old_odds = old_data.get('odds_home', 0)
            new_odds = new_data.get('odds_home', 0)
            
            if old_odds and new_odds:
                return abs((new_odds - old_odds) / old_odds) * 100
            
            # Vérifier si le status a changé
            if old_data.get('status') != new_data.get('status'):
                return 100.0
            
            return 0.0
        
        return 0.0
    except Exception:
        return 0.0
