"""
Endpoints d'analyse sportive.
- GET /api/v1/sports/predict/<match_id>
- GET /api/v1/sports/matches (optionnel)
- GET /api/v1/sports/predictions/history (optionnel)
"""

import json
import logging
from flask import Blueprint, request, jsonify

from app.core.database import db
from app.api.v1.auth import token_required
from app.models.prediction import Prediction
from app.models.consultation import Consultation
from app.services.sports_api_service import sports_api_service
from app.services.prediction_service import prediction_service
from app.services.gpt_service import gpt_service

logger = logging.getLogger(__name__)

# Blueprint
sports_bp = Blueprint('sports', __name__)


@sports_bp.route('/predict/<match_id>', methods=['GET'])
@token_required
def predict_match(current_user, match_id):
    """
    Genere une prediction pour un match sportif.
    
    Args:
        match_id: Identifiant du match.
    
    Returns:
        200: Prediction avec analyse GPT
        404: Match non trouve
        500: Erreur serveur
    
    Response JSON:
        {
            "match": {
                "id": "...",
                "home_team": "...",
                "away_team": "...",
                "competition": "...",
                "date": "...",
                "stats": { ... }
            },
            "model_score": 0.72,
            "gpt_analysis": {
                "domain": "sports",
                "summary": "...",
                "analysis": "...",
                "prediction_type": "probability",
                "prediction_value": 0.68,
                "confidence": 0.7,
                "caveats": "...",
                "educational_reminder": "..."
            }
        }
    """
    # Log de la consultation
    consultation = Consultation(
        user_id=current_user.id,
        consultation_type='sports',
        endpoint=f'/api/v1/sports/predict/{match_id}',
        query_params={'match_id': match_id}
    )
    
    try:
        # Recuperer les donnees du match
        match_data = sports_api_service.get_match_data(match_id)
        
        if not match_data:
            consultation.success = False
            consultation.error_message = 'Match non trouve'
            db.session.add(consultation)
            db.session.commit()
            
            return jsonify({
                'error': 'Match non trouve',
                'message': f'Aucun match trouve avec l\'identifiant {match_id}'
            }), 404
        
        # Calculer le score du modele
        model_score = prediction_service.predict_sport(match_data)
        
        # Obtenir l'analyse GPT
        gpt_analysis = gpt_service.analyse_sport(match_data, model_score)
        
        # Sauvegarder la prediction
        prediction = Prediction(
            user_id=current_user.id,
            prediction_type='sports',
            external_match_id=match_id,
            model_score=model_score,
            prediction_value=str(gpt_analysis.get('prediction_value', '')),
            confidence=gpt_analysis.get('confidence'),
            gpt_analysis=gpt_analysis,
            input_data=match_data
        )
        db.session.add(prediction)
        
        # Log succes
        consultation.success = True
        db.session.add(consultation)
        db.session.commit()
        
        # Construire la reponse
        response = {
            'match': {
                'id': match_data.get('match_id', match_id),
                'home_team': match_data.get('home_team', {}).get('name', 'Unknown'),
                'away_team': match_data.get('away_team', {}).get('name', 'Unknown'),
                'competition': match_data.get('league', 'Unknown'),
                'date': match_data.get('date'),
                'stats': {
                    'home_team': match_data.get('home_team', {}),
                    'away_team': match_data.get('away_team', {}),
                    'odds': match_data.get('odds', {}),
                    'h2h': match_data.get('h2h_stats', {})
                }
            },
            'model_score': model_score,
            'gpt_analysis': gpt_analysis,
            'disclaimer': 'Prediction experimentale a but educatif uniquement.'
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f'Erreur prediction sports: {e}')
        consultation.success = False
        consultation.error_message = str(e)
        db.session.add(consultation)
        db.session.commit()
        
        return jsonify({
            'error': 'Erreur lors de la prediction',
            'message': str(e)
        }), 500


@sports_bp.route('/matches', methods=['GET'])
@token_required
def get_matches(current_user):
    """
    Recupere la liste des matchs disponibles.
    
    Query params:
        sport: Type de sport (default: football)
        league: Ligue specifique (optionnel)
        limit: Nombre max de resultats (default: 20)
    
    Returns:
        200: Liste des matchs
    """
    sport = request.args.get('sport', 'football')
    league = request.args.get('league')
    limit = int(request.args.get('limit', 20))
    
    # Log consultation
    consultation = Consultation(
        user_id=current_user.id,
        consultation_type='sports',
        endpoint='/api/v1/sports/matches',
        query_params={'sport': sport, 'league': league, 'limit': limit}
    )
    
    try:
        matches = sports_api_service.get_upcoming_matches(
            sport=sport,
            league=league,
            limit=limit
        )
        
        consultation.success = True
        db.session.add(consultation)
        db.session.commit()
        
        return jsonify({
            'sport': sport,
            'league': league,
            'matches': matches,
            'count': len(matches)
        }), 200
    
    except Exception as e:
        logger.error(f'Erreur recuperation matchs: {e}')
        consultation.success = False
        consultation.error_message = str(e)
        db.session.add(consultation)
        db.session.commit()
        
        return jsonify({
            'error': 'Erreur lors de la recuperation des matchs',
            'message': str(e)
        }), 500


@sports_bp.route('/predictions/history', methods=['GET'])
@token_required
def get_predictions_history(current_user):
    """
    Recupere l'historique des predictions de l'utilisateur.
    
    Query params:
        limit: Nombre max de resultats (default: 20)
        offset: Offset pour pagination (default: 0)
    
    Returns:
        200: Liste des predictions
    """
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    predictions = Prediction.query.filter_by(
        user_id=current_user.id,
        prediction_type='sports'
    ).order_by(
        Prediction.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    total = Prediction.query.filter_by(
        user_id=current_user.id,
        prediction_type='sports'
    ).count()
    
    return jsonify({
        'predictions': [p.to_dict() for p in predictions],
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200
