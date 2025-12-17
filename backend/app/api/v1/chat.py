"""
API Chat IA - Assistant d'analyse PredictWise.
Endpoint conversationnel pour le copilote décisionnel.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime

from app.services.chat_service import chat_service

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/message', methods=['POST'])
@jwt_required()
def send_message():
    """
    Envoie un message au copilote IA et reçoit une réponse.
    
    Body:
        message (str): Message de l'utilisateur
        context (dict, optional): Contexte additionnel (analyse en cours, etc.)
        conversation_id (str, optional): ID de la conversation pour historique
    
    Returns:
        JSON avec la réponse de l'assistant
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message requis'}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({'error': 'Message vide'}), 400
        
        if len(user_message) > 2000:
            return jsonify({'error': 'Message trop long (max 2000 caractères)'}), 400
        
        context = data.get('context', {})
        conversation_id = data.get('conversation_id')
        
        # Appeler le service de chat
        response = chat_service.process_message(
            user_id=user_id,
            message=user_message,
            context=context,
            conversation_id=conversation_id
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Erreur chat: {e}")
        return jsonify({
            'error': 'Erreur de traitement',
            'response': {
                'content': "Je suis momentanément indisponible. Veuillez réessayer.",
                'type': 'error'
            }
        }), 500


@chat_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """
    Récupère l'historique des conversations de l'utilisateur.
    
    Query params:
        limit (int): Nombre de messages (default 50)
        conversation_id (str, optional): Filtrer par conversation
    
    Returns:
        Liste des messages de l'historique
    """
    try:
        user_id = get_jwt_identity()
        limit = min(int(request.args.get('limit', 50)), 100)
        conversation_id = request.args.get('conversation_id')
        
        history = chat_service.get_conversation_history(
            user_id=user_id,
            limit=limit,
            conversation_id=conversation_id
        )
        
        return jsonify({
            'history': history,
            'count': len(history)
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur récupération historique: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500


@chat_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_history():
    """Efface l'historique des conversations de l'utilisateur."""
    try:
        user_id = get_jwt_identity()
        conversation_id = request.args.get('conversation_id')
        
        chat_service.clear_history(
            user_id=user_id,
            conversation_id=conversation_id
        )
        
        return jsonify({'message': 'Historique effacé'}), 200
        
    except Exception as e:
        logger.error(f"Erreur suppression historique: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500


@chat_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def get_suggestions():
    """
    Récupère des suggestions de questions basées sur le contexte.
    
    Query params:
        domain (str): 'sports' ou 'finance'
    
    Returns:
        Liste de suggestions de questions
    """
    domain = request.args.get('domain', 'general')
    
    suggestions = chat_service.get_suggestions(domain)
    
    return jsonify({
        'suggestions': suggestions,
        'domain': domain
    }), 200
