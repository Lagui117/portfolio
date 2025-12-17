"""
Endpoints d'analyse financiere.
- GET /api/v1/finance/predict/<ticker>
- GET /api/v1/finance/stocks (optionnel)
- GET /api/v1/finance/predictions/history (optionnel)
"""

import json
import logging
from flask import Blueprint, request, jsonify

from app.core.database import db
from app.api.v1.auth import token_required
from app.models.prediction import Prediction
from app.models.consultation import Consultation
from app.services.finance_api_service import finance_api_service
from app.services.prediction_service import prediction_service
from app.services.gpt_service import gpt_service

logger = logging.getLogger(__name__)

# Blueprint
finance_bp = Blueprint('finance', __name__)


@finance_bp.route('/predict/<ticker>', methods=['GET'])
@token_required
def predict_stock(current_user, ticker):
    """
    Genere une prediction pour un actif financier.
    
    Args:
        ticker: Symbole boursier (ex: AAPL, GOOGL).
    
    Returns:
        200: Prediction avec analyse GPT
        404: Ticker non trouve
        500: Erreur serveur
    
    Response JSON:
        {
            "asset": {
                "ticker": "...",
                "name": "...",
                "prices": [...],
                "indicators": { ... }
            },
            "model_score": 0.64,
            "gpt_analysis": {
                "domain": "finance",
                "summary": "...",
                "analysis": "...",
                "prediction_type": "trend",
                "prediction_value": "UP" ou "DOWN" ou "NEUTRAL",
                "confidence": 0.6,
                "caveats": "...",
                "disclaimer": "..."
            }
        }
    """
    ticker = ticker.upper().strip()
    period = request.args.get('period', '1mo')
    
    # Log de la consultation
    consultation = Consultation(
        user_id=current_user.id,
        consultation_type='finance',
        endpoint=f'/api/v1/finance/predict/{ticker}',
        query_params={'ticker': ticker, 'period': period}
    )
    
    try:
        # Recuperer les donnees boursieres
        stock_data = finance_api_service.get_stock_data(ticker, period)
        
        if not stock_data:
            consultation.success = False
            consultation.error_message = 'Ticker non trouve'
            db.session.add(consultation)
            db.session.commit()
            
            return jsonify({
                'error': 'Ticker non trouve',
                'message': f'Aucune donnee trouvee pour le symbole {ticker}'
            }), 404
        
        # Calculer le score/tendance du modele
        model_score = prediction_service.predict_stock(stock_data)
        
        # Obtenir l'analyse GPT
        gpt_analysis = gpt_service.analyse_finance(stock_data, model_score)
        
        # Sauvegarder la prediction
        prediction = Prediction(
            user_id=current_user.id,
            prediction_type='finance',
            ticker=ticker,
            model_score=model_score if isinstance(model_score, (int, float)) else None,
            prediction_value=str(gpt_analysis.get('prediction_value', '')),
            confidence=gpt_analysis.get('confidence'),
            gpt_analysis=gpt_analysis,
            input_data=stock_data
        )
        db.session.add(prediction)
        
        # Log succes
        consultation.success = True
        db.session.add(consultation)
        db.session.commit()
        
        # Construire la reponse
        response = {
            'asset': {
                'ticker': stock_data.get('symbol', ticker),
                'name': stock_data.get('name', ticker),
                'sector': stock_data.get('sector'),
                'industry': stock_data.get('industry'),
                'current_price': stock_data.get('current_price'),
                'prices': stock_data.get('prices', []),
                'indicators': stock_data.get('indicators', {})
            },
            'model_score': model_score,
            'gpt_analysis': gpt_analysis,
            'disclaimer': 'Analyse à titre informatif. Ne constitue pas un conseil d\'investissement.'
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f'Erreur prediction finance: {e}')
        consultation.success = False
        consultation.error_message = str(e)
        db.session.add(consultation)
        db.session.commit()
        
        return jsonify({
            'error': 'Erreur lors de la prediction',
            'message': str(e)
        }), 500


@finance_bp.route('/stocks', methods=['GET'])
@token_required
def get_popular_stocks(current_user):
    """
    Recupere une liste d'actifs populaires.
    
    Query params:
        sector: Secteur specifique (optionnel)
        limit: Nombre max de resultats (default: 20)
    
    Returns:
        200: Liste des actifs
    """
    sector = request.args.get('sector')
    limit = int(request.args.get('limit', 20))
    
    # Log consultation
    consultation = Consultation(
        user_id=current_user.id,
        consultation_type='finance',
        endpoint='/api/v1/finance/stocks',
        query_params={'sector': sector, 'limit': limit}
    )
    
    try:
        stocks = finance_api_service.get_popular_stocks(sector=sector, limit=limit)
        
        consultation.success = True
        db.session.add(consultation)
        db.session.commit()
        
        return jsonify({
            'sector': sector,
            'stocks': stocks,
            'count': len(stocks)
        }), 200
    
    except Exception as e:
        logger.error(f'Erreur recuperation actifs: {e}')
        consultation.success = False
        consultation.error_message = str(e)
        db.session.add(consultation)
        db.session.commit()
        
        return jsonify({
            'error': 'Erreur lors de la recuperation des actifs',
            'message': str(e)
        }), 500


@finance_bp.route('/predictions/history', methods=['GET'])
@token_required
def get_predictions_history(current_user):
    """
    Recupere l'historique des predictions financieres de l'utilisateur.
    
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
        prediction_type='finance'
    ).order_by(
        Prediction.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    total = Prediction.query.filter_by(
        user_id=current_user.id,
        prediction_type='finance'
    ).count()
    
    return jsonify({
        'predictions': [p.to_dict() for p in predictions],
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200
