"""Sports endpoints with ML predictions."""
from flask import request
from flask_restx import Namespace, Resource, fields
from app.api.v1.auth import token_required
from app.services.sports_service import SportsService
from app.core.database import db
from app.models.consultation import Consultation
from app.models.prediction import Prediction
import json

# Create namespace
api = Namespace('sports', description='Sports data and ML predictions')

# Initialize service
sports_service = SportsService()

# Define models for Swagger
match_model = api.model('Match', {
    'id': fields.Integer(description='Match ID'),
    'sport_type': fields.String(description='Sport type'),
    'league': fields.String(description='League name'),
    'home_team': fields.String(description='Home team'),
    'away_team': fields.String(description='Away team'),
    'event_date': fields.String(description='Match date (ISO format)'),
    'status': fields.String(description='Match status'),
    'odds': fields.Raw(description='Betting odds'),
})

prediction_input = api.model('SportsPredictionInput', {
    'home_team': fields.String(required=True, description='Home team name', example='Manchester United'),
    'away_team': fields.String(required=True, description='Away team name', example='Liverpool'),
    'sport': fields.String(required=True, description='Sport type', example='football'),
    'league': fields.String(description='League name', example='Premier League'),
})

prediction_result = api.model('PredictionResult', {
    'result': fields.String(description='Predicted result (HOME_WIN/DRAW/AWAY_WIN)'),
    'confidence': fields.Float(description='Confidence score'),
    'probabilities': fields.Raw(description='Probabilities for each outcome'),
    'model_version': fields.String(description='ML model version'),
})


@api.route('/matches')
class Matches(Resource):
    """Get sports matches."""
    
    @token_required
    @api.doc(
        params={
            'sport': 'Sport type (football, basketball, etc.)',
            'league': 'League name',
            'days_ahead': 'Number of days to look ahead (default: 7)',
            'limit': 'Maximum results (default: 20)'
        },
        security='Bearer'
    )
    @api.response(200, 'Success', [match_model])
    @api.response(401, 'Unauthorized')
    def get(self, current_user):
        """Retrieve upcoming sports matches.
        
        Returns a list of upcoming matches with odds and details.
        Logs the consultation in the database.
        """
        sport = request.args.get('sport', 'football')
        league = request.args.get('league')
        days_ahead = int(request.args.get('days_ahead', 7))
        limit = int(request.args.get('limit', 20))
        
        # Log consultation
        consultation = Consultation(
            user_id=current_user.id,
            consultation_type='sports',
            endpoint='/api/v1/sports/matches',
            query_params=json.dumps(request.args.to_dict())
        )
        db.session.add(consultation)
        db.session.commit()
        
        # Fetch matches
        matches = sports_service.get_upcoming_matches(
            sport=sport,
            league=league,
            days_ahead=days_ahead,
            limit=limit
        )
        
        return {
            'sport': sport,
            'league': league,
            'matches': matches,
            'count': len(matches)
        }, 200


@api.route('/matches/<int:event_id>')
class MatchDetail(Resource):
    """Get specific match details."""
    
    @token_required
    @api.response(200, 'Success', match_model)
    @api.response(404, 'Match not found')
    def get(self, current_user, event_id):
        """Retrieve details for a specific match by ID."""
        match = sports_service.get_match_by_id(event_id)
        
        if not match:
            return {'error': 'Match non trouvé'}, 404
        
        return {'match': match}, 200


@api.route('/statistics/<string:team_name>')
class TeamStatistics(Resource):
    """Get team statistics."""
    
    @token_required
    @api.doc(
        params={'sport': 'Sport type (default: football)', 'season': 'Season (e.g., 2024-2025)'},
        security='Bearer'
    )
    @api.response(200, 'Success')
    def get(self, current_user, team_name):
        """Retrieve statistics for a specific team.
        
        Returns win rate, goals, form, and other metrics.
        """
        sport = request.args.get('sport', 'football')
        season = request.args.get('season')
        
        # Log consultation
        consultation = Consultation(
            user_id=current_user.id,
            consultation_type='sports',
            endpoint=f'/api/v1/sports/statistics/{team_name}',
            query_params=json.dumps({'sport': sport, 'season': season})
        )
        db.session.add(consultation)
        db.session.commit()
        
        # Fetch statistics
        stats = sports_service.get_team_statistics(
            team_name=team_name,
            sport=sport,
            season=season
        )
        
        return {
            'team': team_name,
            'sport': sport,
            'statistics': stats
        }, 200


@api.route('/predict')
class Predict(Resource):
    """Predict sports match outcome using ML."""
    
    @token_required
    @api.expect(prediction_input, validate=True)
    @api.response(200, 'Prediction generated', prediction_result)
    @api.response(400, 'Invalid input')
    def post(self, current_user):
        """Generate ML prediction for a sports match.
        
        Uses trained Random Forest model to predict match outcome.
        Considers team statistics, form, and historical data.
        Saves prediction to database for tracking.
        """
        data = request.get_json()
        
        # Validate required fields
        required = ['home_team', 'away_team', 'sport']
        if not all(k in data for k in required):
            return {
                'error': 'Champs manquants',
                'required': required
            }, 400
        
        # Generate prediction
        try:
            prediction = sports_service.predict_match_outcome(
                home_team=data['home_team'],
                away_team=data['away_team'],
                sport=data['sport'],
                league=data.get('league'),
                additional_features=data.get('features', {})
            )
            
            # Save prediction to database
            pred_record = Prediction(
                user_id=current_user.id,
                prediction_type='sports',
                input_data=json.dumps({
                    'home_team': data['home_team'],
                    'away_team': data['away_team'],
                    'sport': data['sport'],
                    'league': data.get('league')
                }),
                prediction_result=prediction['result'],
                confidence_score=prediction.get('confidence'),
                model_version=prediction.get('model_version', 'v1.0')
            )
            db.session.add(pred_record)
            db.session.commit()
            
            return {
                'prediction': prediction,
                'prediction_id': pred_record.id,
                'match': {
                    'home_team': data['home_team'],
                    'away_team': data['away_team'],
                    'sport': data['sport']
                }
            }, 200
            
        except Exception as e:
            return {
                'error': 'Erreur lors de la prédiction',
                'details': str(e)
            }, 500


@api.route('/predictions/history')
class PredictionHistory(Resource):
    """Get user's sports prediction history."""
    
    @token_required
    @api.doc(params={'limit': 'Max results (default: 50)'}, security='Bearer')
    @api.response(200, 'Success')
    def get(self, current_user):
        """Retrieve user's sports prediction history.
        
        Returns list of past predictions with results and confidence.
        """
        limit = int(request.args.get('limit', 50))
        
        predictions = Prediction.query.filter_by(
            user_id=current_user.id,
            prediction_type='sports'
        ).order_by(Prediction.created_at.desc()).limit(limit).all()
        
        results = []
        for pred in predictions:
            pred_dict = pred.to_dict()
            # Parse input data
            try:
                pred_dict['match_details'] = json.loads(pred.input_data)
            except:
                pred_dict['match_details'] = {}
            results.append(pred_dict)
        
        return {
            'predictions': results,
            'count': len(results),
            'total': Prediction.query.filter_by(
                user_id=current_user.id,
                prediction_type='sports'
            ).count()
        }, 200
