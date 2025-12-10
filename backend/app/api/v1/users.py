"""
Endpoints API pour les statistiques utilisateur et suggestions IA
"""
from flask_restx import Namespace, Resource
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.core.database import get_db
from app.models.user import User
from app.models.prediction import Prediction
from app.models.consultation import Consultation
from sqlalchemy import func

api = Namespace('users', description='Opérations utilisateur')


@api.route('/stats')
class UserStats(Resource):
    @jwt_required()
    def get(self):
        """
        Récupère les statistiques de l'utilisateur connecté
        """
        current_user_id = get_jwt_identity()
        db = next(get_db())
        
        try:
            # Récupérer l'utilisateur
            user = db.query(User).filter(User.id == current_user_id).first()
            if not user:
                return {'error': 'Utilisateur non trouvé'}, 404
            
            # Compter les prédictions par catégorie
            total_predictions = db.query(func.count(Prediction.id)).filter(
                Prediction.user_id == current_user_id
            ).scalar() or 0
            
            sports_predictions = db.query(func.count(Prediction.id)).filter(
                Prediction.user_id == current_user_id,
                Prediction.category == 'sports'
            ).scalar() or 0
            
            finance_predictions = db.query(func.count(Prediction.id)).filter(
                Prediction.user_id == current_user_id,
                Prediction.category == 'finance'
            ).scalar() or 0
            
            # Compter les consultations
            total_consultations = db.query(func.count(Consultation.id)).filter(
                Consultation.user_id == current_user_id
            ).scalar() or 0
            
            return {
                'total_predictions': total_predictions,
                'sports_predictions': sports_predictions,
                'finance_predictions': finance_predictions,
                'total_consultations': total_consultations,
                'member_since': user.created_at.isoformat() if user.created_at else None
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
