"""
API Dashboard Utilisateur Avancé.
Endpoints pour les statistiques personnalisées, KPIs et historique de performance.
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func, desc, case
from datetime import datetime, timedelta, timezone
import logging

from app.core.database import db
from app.models.user import User
from app.models.prediction import Prediction
from app.models.consultation import Consultation
from app.api.v1.auth import token_required

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/overview', methods=['GET'])
@token_required
def get_overview(current_user):
    """
    Résumé complet du dashboard utilisateur.
    
    Returns:
        - stats: KPIs principaux
        - recent_predictions: 5 dernières prédictions
        - performance: métriques de performance
        - activity: activité récente
    """
    user_id = current_user.id
    
    try:
        # Stats de base
        total_predictions = Prediction.query.filter_by(user_id=user_id).count()
        total_consultations = Consultation.query.filter_by(user_id=user_id).count()
        
        sports_predictions = Prediction.query.filter_by(
            user_id=user_id, 
            prediction_type='sports'
        ).count()
        
        finance_predictions = Prediction.query.filter_by(
            user_id=user_id, 
            prediction_type='finance'
        ).count()
        
        # Confiance moyenne
        avg_confidence = db.session.query(
            func.avg(Prediction.confidence)
        ).filter(
            Prediction.user_id == user_id,
            Prediction.confidence.isnot(None)
        ).scalar() or 0
        
        # Dernières prédictions
        recent_predictions = Prediction.query.filter_by(
            user_id=user_id
        ).order_by(
            desc(Prediction.created_at)
        ).limit(5).all()
        
        # Activité des 7 derniers jours
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        predictions_this_week = Prediction.query.filter(
            Prediction.user_id == user_id,
            Prediction.created_at >= week_ago
        ).count()
        
        # Répartition par type
        type_distribution = {
            'sports': sports_predictions,
            'finance': finance_predictions
        }
        
        return jsonify({
            'stats': {
                'total_predictions': total_predictions,
                'total_consultations': total_consultations,
                'sports_predictions': sports_predictions,
                'finance_predictions': finance_predictions,
                'avg_confidence': round(avg_confidence * 100, 1) if avg_confidence else 0,
                'predictions_this_week': predictions_this_week
            },
            'recent_predictions': [p.to_dict() for p in recent_predictions],
            'type_distribution': type_distribution,
            'performance': {
                'win_rate': None,  # À implémenter avec les résultats réels
                'roi_theoretical': None,
                'accuracy_trend': 'stable'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur dashboard overview: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500


@dashboard_bp.route('/performance', methods=['GET'])
@token_required
def get_performance(current_user):
    """
    Métriques de performance détaillées.
    
    Query params:
        - period: '7d', '30d', '90d', 'all' (default: '30d')
        - type: 'sports', 'finance', 'all' (default: 'all')
    
    Returns:
        - daily_activity: activité par jour
        - confidence_distribution: répartition des scores de confiance
        - by_type: performance par type de prédiction
        - trends: tendances (hausse/baisse)
    """
    user_id = current_user.id
    period = request.args.get('period', '30d')
    pred_type = request.args.get('type', 'all')
    
    # Calculer la date de début
    period_days = {
        '7d': 7,
        '30d': 30,
        '90d': 90,
        'all': 365 * 10  # Tout l'historique
    }
    days = period_days.get(period, 30)
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    try:
        # Query de base
        query = Prediction.query.filter(
            Prediction.user_id == user_id,
            Prediction.created_at >= start_date
        )
        
        if pred_type != 'all':
            query = query.filter(Prediction.prediction_type == pred_type)
        
        predictions = query.all()
        
        # Activité quotidienne
        daily_activity = {}
        confidence_buckets = {'low': 0, 'medium': 0, 'high': 0}
        
        for pred in predictions:
            # Activité par jour
            day_key = pred.created_at.strftime('%Y-%m-%d')
            daily_activity[day_key] = daily_activity.get(day_key, 0) + 1
            
            # Distribution confiance
            if pred.confidence:
                if pred.confidence < 0.5:
                    confidence_buckets['low'] += 1
                elif pred.confidence < 0.75:
                    confidence_buckets['medium'] += 1
                else:
                    confidence_buckets['high'] += 1
        
        # Stats par type
        by_type = {}
        for t in ['sports', 'finance']:
            type_preds = [p for p in predictions if p.prediction_type == t]
            if type_preds:
                confidences = [p.confidence for p in type_preds if p.confidence]
                by_type[t] = {
                    'count': len(type_preds),
                    'avg_confidence': round(sum(confidences) / len(confidences) * 100, 1) if confidences else 0
                }
        
        # Tendance (comparer avec période précédente)
        prev_start = start_date - timedelta(days=days)
        prev_count = Prediction.query.filter(
            Prediction.user_id == user_id,
            Prediction.created_at >= prev_start,
            Prediction.created_at < start_date
        ).count()
        
        current_count = len(predictions)
        if prev_count > 0:
            trend_pct = ((current_count - prev_count) / prev_count) * 100
        else:
            trend_pct = 100 if current_count > 0 else 0
        
        return jsonify({
            'period': period,
            'total_predictions': current_count,
            'daily_activity': daily_activity,
            'confidence_distribution': confidence_buckets,
            'by_type': by_type,
            'trend': {
                'direction': 'up' if trend_pct > 0 else ('down' if trend_pct < 0 else 'stable'),
                'percentage': round(abs(trend_pct), 1),
                'previous_period_count': prev_count
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur performance: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500


@dashboard_bp.route('/history', methods=['GET'])
@token_required
def get_prediction_history(current_user):
    """
    Historique complet des prédictions avec filtres.
    
    Query params:
        - page: numéro de page (default: 1)
        - per_page: résultats par page (default: 20, max: 100)
        - type: 'sports', 'finance', 'all'
        - confidence_min: score minimum (0-1)
        - confidence_max: score maximum (0-1)
        - start_date: date de début (ISO format)
        - end_date: date de fin (ISO format)
        - sort: 'date', 'confidence' (default: 'date')
        - order: 'asc', 'desc' (default: 'desc')
    """
    user_id = current_user.id
    
    # Paramètres de pagination
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # Filtres
    pred_type = request.args.get('type', 'all')
    confidence_min = request.args.get('confidence_min', type=float)
    confidence_max = request.args.get('confidence_max', type=float)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sort_by = request.args.get('sort', 'date')
    order = request.args.get('order', 'desc')
    
    try:
        query = Prediction.query.filter_by(user_id=user_id)
        
        # Appliquer les filtres
        if pred_type != 'all':
            query = query.filter(Prediction.prediction_type == pred_type)
        
        if confidence_min is not None:
            query = query.filter(Prediction.confidence >= confidence_min)
        
        if confidence_max is not None:
            query = query.filter(Prediction.confidence <= confidence_max)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(Prediction.created_at >= start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(Prediction.created_at <= end_dt)
            except ValueError:
                pass
        
        # Tri
        if sort_by == 'confidence':
            sort_col = Prediction.confidence
        else:
            sort_col = Prediction.created_at
        
        if order == 'asc':
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'predictions': [p.to_dict() for p in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters_applied': {
                'type': pred_type,
                'confidence_range': [confidence_min, confidence_max],
                'date_range': [start_date, end_date]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur history: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500


@dashboard_bp.route('/favorites', methods=['GET'])
@token_required
def get_favorites(current_user):
    """
    Récupère les équipes/actifs les plus consultés par l'utilisateur.
    """
    user_id = current_user.id
    
    try:
        # Top actifs finance
        finance_favorites = db.session.query(
            Prediction.ticker,
            func.count(Prediction.id).label('count')
        ).filter(
            Prediction.user_id == user_id,
            Prediction.prediction_type == 'finance',
            Prediction.ticker.isnot(None)
        ).group_by(
            Prediction.ticker
        ).order_by(
            desc('count')
        ).limit(5).all()
        
        # Top sports (via external_match_id pattern)
        sports_favorites = db.session.query(
            Prediction.external_match_id,
            func.count(Prediction.id).label('count')
        ).filter(
            Prediction.user_id == user_id,
            Prediction.prediction_type == 'sports',
            Prediction.external_match_id.isnot(None)
        ).group_by(
            Prediction.external_match_id
        ).order_by(
            desc('count')
        ).limit(5).all()
        
        return jsonify({
            'finance': [
                {'ticker': f[0], 'prediction_count': f[1]}
                for f in finance_favorites if f[0]
            ],
            'sports': [
                {'match_id': s[0], 'prediction_count': s[1]}
                for s in sports_favorites if s[0]
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur favorites: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500


@dashboard_bp.route('/kpis', methods=['GET'])
@token_required
def get_kpis(current_user):
    """
    KPIs avancés pour le dashboard.
    
    Returns:
        - win_rate: taux de réussite (si résultats disponibles)
        - avg_confidence: confiance moyenne IA
        - activity_score: score d'activité
        - favorite_domain: domaine préféré (sports/finance)
        - streak: série actuelle
    """
    user_id = current_user.id
    
    try:
        predictions = Prediction.query.filter_by(user_id=user_id).all()
        
        if not predictions:
            return jsonify({
                'win_rate': None,
                'avg_confidence': 0,
                'activity_score': 0,
                'favorite_domain': None,
                'streak': 0,
                'total_predictions': 0
            }), 200
        
        # Confiance moyenne
        confidences = [p.confidence for p in predictions if p.confidence]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Domaine préféré
        sports_count = sum(1 for p in predictions if p.prediction_type == 'sports')
        finance_count = len(predictions) - sports_count
        favorite_domain = 'sports' if sports_count > finance_count else 'finance'
        
        # Score d'activité (basé sur les 30 derniers jours)
        month_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_preds = [p for p in predictions if p.created_at and p.created_at >= month_ago]
        activity_score = min(len(recent_preds) / 30 * 100, 100)  # Max 100
        
        # Streak (jours consécutifs avec au moins une prédiction)
        streak = 0
        if predictions:
            dates = sorted(set(p.created_at.date() for p in predictions if p.created_at), reverse=True)
            today = datetime.now(timezone.utc).date()
            
            for i, date in enumerate(dates):
                expected_date = today - timedelta(days=i)
                if date == expected_date:
                    streak += 1
                else:
                    break
        
        return jsonify({
            'win_rate': None,  # À implémenter avec résultats réels
            'avg_confidence': round(avg_confidence * 100, 1),
            'activity_score': round(activity_score, 1),
            'favorite_domain': favorite_domain,
            'streak': streak,
            'total_predictions': len(predictions),
            'domain_split': {
                'sports': sports_count,
                'finance': finance_count
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur KPIs: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500
