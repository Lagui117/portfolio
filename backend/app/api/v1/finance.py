"""Finance endpoints with ML predictions and technical analysis."""
from flask import request
from flask_restx import Namespace, Resource, fields
from app.api.v1.auth import token_required
from app.services.finance_service import FinanceService
from app.services.finance_api_service import finance_api_service
from app.services.gpt_service import gpt_service
from app.services.prediction_service import get_prediction_service
from app.core.database import db
from app.models.consultation import Consultation
from app.models.prediction import Prediction
import json
import logging

logger = logging.getLogger(__name__)

# Create namespace
api = Namespace('finance', description='Financial data and ML predictions')

# Initialize services
finance_service = FinanceService()
prediction_service = get_prediction_service()

# Define models for Swagger
stock_data_model = api.model('StockData', {
    'date': fields.String(description='Date (ISO format)'),
    'open': fields.Float(description='Opening price'),
    'high': fields.Float(description='Highest price'),
    'low': fields.Float(description='Lowest price'),
    'close': fields.Float(description='Closing price'),
    'volume': fields.Integer(description='Trading volume'),
})

indicators_model = api.model('TechnicalIndicators', {
    'MA_5': fields.Float(description='5-day moving average'),
    'MA_20': fields.Float(description='20-day moving average'),
    'MA_50': fields.Float(description='50-day moving average'),
    'RSI': fields.Float(description='Relative Strength Index'),
    'volatility_daily': fields.Float(description='Daily volatility'),
    'volatility_annual': fields.Float(description='Annualized volatility'),
    'current_price': fields.Float(description='Current price'),
})

prediction_input = api.model('FinancePredictionInput', {
    'symbol': fields.String(required=True, description='Stock symbol', example='AAPL'),
    'period': fields.String(description='Analysis period', example='1mo'),
})

prediction_result = api.model('FinancePredictionResult', {
    'symbol': fields.String(description='Stock symbol'),
    'trend': fields.String(description='Predicted trend (UP/DOWN)'),
    'confidence': fields.Float(description='Confidence score'),
    'probabilities': fields.Raw(description='Probabilities for each outcome'),
    'model_version': fields.String(description='ML model version'),
})


@api.route('/stocks/<string:symbol>')
class StockData(Resource):
    """Get stock market data."""
    
    @token_required
    @api.doc(
        params={
            'period': 'Time period (1d, 5d, 1mo, 3mo, 6mo, 1y) - default: 1mo',
            'interval': 'Data interval (1m, 5m, 1h, 1d) - default: 1d'
        },
        security='Bearer'
    )
    @api.response(200, 'Success', [stock_data_model])
    @api.response(401, 'Unauthorized')
    @api.response(404, 'Symbol not found')
    def get(self, current_user, symbol):
        """Retrieve historical stock data for a symbol.
        
        Returns OHLCV (Open, High, Low, Close, Volume) data.
        Logs the consultation in the database.
        """
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', '1d')
        
        # Validate symbol
        if not symbol or len(symbol) > 10:
            return {'error': 'Symbole invalide'}, 400
        
        # Log consultation
        consultation = Consultation(
            user_id=current_user.id,
            consultation_type='finance',
            endpoint=f'/api/v1/finance/stocks/{symbol}',
            query_params=json.dumps({'period': period, 'interval': interval})
        )
        db.session.add(consultation)
        db.session.commit()
        
        # Fetch stock data
        try:
            stock_data = finance_service.get_stock_data(
                symbol=symbol.upper(),
                period=period,
                interval=interval
            )
            
            return {
                'symbol': symbol.upper(),
                'period': period,
                'interval': interval,
                'data': stock_data,
                'count': len(stock_data)
            }, 200
            
        except Exception as e:
            return {
                'error': 'Erreur lors de la récupération des données',
                'details': str(e)
            }, 500


@api.route('/indicators/<string:symbol>')
class TechnicalIndicators(Resource):
    """Get technical indicators."""
    
    @token_required
    @api.doc(
        params={
            'period': 'Time period for calculation (default: 1mo)',
            'indicators': 'Comma-separated list: MA,RSI,VOLATILITY,MACD'
        },
        security='Bearer'
    )
    @api.response(200, 'Success', indicators_model)
    def get(self, current_user, symbol):
        """Calculate technical indicators for a stock.
        
        Available indicators:
        - MA: Moving Averages (5, 20, 50 days)
        - RSI: Relative Strength Index
        - VOLATILITY: Daily and annualized volatility
        - MACD: Moving Average Convergence Divergence
        """
        period = request.args.get('period', '1mo')
        indicators_str = request.args.get('indicators', 'MA,RSI,VOLATILITY')
        indicators = [i.strip().upper() for i in indicators_str.split(',')]
        
        # Log consultation
        consultation = Consultation(
            user_id=current_user.id,
            consultation_type='finance',
            endpoint=f'/api/v1/finance/indicators/{symbol}',
            query_params=json.dumps({'period': period, 'indicators': indicators})
        )
        db.session.add(consultation)
        db.session.commit()
        
        # Calculate indicators
        try:
            result = finance_service.calculate_indicators(
                symbol=symbol.upper(),
                period=period,
                indicators=indicators
            )
            
            if not result:
                return {
                    'error': 'Impossible de calculer les indicateurs',
                    'symbol': symbol.upper()
                }, 404
            
            return {
                'symbol': symbol.upper(),
                'period': period,
                'indicators': result
            }, 200
            
        except Exception as e:
            return {
                'error': 'Erreur lors du calcul des indicateurs',
                'details': str(e)
            }, 500


@api.route('/predict')
class Predict(Resource):
    """Predict stock price trend using ML."""
    
    @token_required
    @api.expect(prediction_input, validate=True)
    @api.response(200, 'Prediction generated', prediction_result)
    @api.response(400, 'Invalid input')
    def post(self, current_user):
        """Generate ML prediction for stock price trend (UP/DOWN).
        
        Uses Logistic Regression with technical indicators.
        Analyzes moving averages, RSI, and volatility.
        Saves prediction to database for tracking.
        """
        data = request.get_json()
        
        if 'symbol' not in data:
            return {'error': 'Le champ "symbol" est requis'}, 400
        
        symbol = data['symbol'].upper()
        period = data.get('period', '1mo')
        
        # Generate prediction
        try:
            prediction = finance_service.predict_trend(
                symbol=symbol,
                period=period
            )
            
            # Check if there was an error
            if 'error' in prediction:
                return prediction, 400
            
            # Save prediction to database
            pred_record = Prediction(
                user_id=current_user.id,
                prediction_type='finance',
                input_data=json.dumps({
                    'symbol': symbol,
                    'period': period
                }),
                prediction_result=prediction['trend'],
                confidence_score=prediction.get('confidence'),
                model_version=prediction.get('model_version', 'v1.0')
            )
            db.session.add(pred_record)
            db.session.commit()
            
            return {
                'prediction': prediction,
                'prediction_id': pred_record.id,
                'timestamp': pred_record.created_at.isoformat()
            }, 200
            
        except Exception as e:
            return {
                'error': 'Erreur lors de la prédiction',
                'details': str(e)
            }, 500


@api.route('/predictions/history')
class PredictionHistory(Resource):
    """Get user's finance prediction history."""
    
    @token_required
    @api.doc(params={'limit': 'Max results (default: 50)'}, security='Bearer')
    @api.response(200, 'Success')
    def get(self, current_user):
        """Retrieve user's finance prediction history.
        
        Returns list of past predictions with results, confidence, and timestamps.
        """
        limit = int(request.args.get('limit', 50))
        
        predictions = Prediction.query.filter_by(
            user_id=current_user.id,
            prediction_type='finance'
        ).order_by(Prediction.created_at.desc()).limit(limit).all()
        
        results = []
        for pred in predictions:
            pred_dict = pred.to_dict()
            # Parse input data
            try:
                pred_dict['input_details'] = json.loads(pred.input_data)
            except:
                pred_dict['input_details'] = {}
            results.append(pred_dict)
        
        return {
            'predictions': results,
            'count': len(results),
            'total': Prediction.query.filter_by(
                user_id=current_user.id,
                prediction_type='finance'
            ).count()
        }, 200


@api.route('/predict/<string:ticker>')
class FinancePrediction(Resource):
    """Get comprehensive financial prediction with GPT analysis."""
    
    @token_required
    @api.doc(
        security='Bearer',
        params={
            'period': 'Time period for analysis (default: 1mo)'
        },
        description="""Generate a comprehensive financial prediction combining:
        - Stock market data and technical indicators
        - Internal ML model prediction
        - GPT-powered analysis and insights
        
        IMPORTANT: This is an EDUCATIONAL tool. Do not use for actual investment decisions."""
    )
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    @api.response(404, 'Ticker not found')
    @api.response(500, 'Server error')
    def get(self, current_user, ticker):
        """
        Generate comprehensive prediction for a stock.
        
        This endpoint combines multiple data sources:
        1. Stock data from finance API (yfinance or alternative)
        2. Technical indicators calculation
        3. ML model prediction
        4. GPT analysis
        
        Returns a complete prediction with educational context.
        """
        try:
            period = request.args.get('period', '1mo')
            ticker = ticker.upper().strip()
            
            # 1. Fetch stock data from API
            try:
                stock_data = finance_api_service.get_stock_data(ticker, period)
            except Exception as e:
                return {
                    'error': 'Failed to fetch stock data',
                    'details': str(e),
                    'ticker': ticker
                }, 404
            
            # 2. Extract indicators for ML prediction
            indicators = stock_data.get('indicators', {})
            
            # 3. Get ML prediction
            ml_result = None
            ml_score = None
            try:
                ml_result = prediction_service.predict_stock_movement(indicators)
                ml_score = ml_result.get('prediction')
            except Exception as e:
                logger.error(f"ML prediction failed: {e}")
                ml_result = {'error': 'ML prediction unavailable'}
            
            # 4. Get GPT analysis
            gpt_analysis = None
            try:
                gpt_analysis = gpt_service.analyse_finance(stock_data, ml_score)
            except Exception as e:
                logger.error(f"GPT analysis failed: {e}")
                gpt_analysis = {
                    'error': 'GPT analysis unavailable',
                    'educational_reminder': 'This is an educational platform. Do not use for real investments.'
                }
            
            # 5. Log consultation
            consultation = Consultation(
                user_id=current_user.id,
                consultation_type='finance',
                endpoint=f'/api/v1/finance/predict/{ticker}',
                query_params=json.dumps({'ticker': ticker, 'period': period})
            )
            db.session.add(consultation)
            
            # 6. Save prediction
            prediction = Prediction(
                user_id=current_user.id,
                prediction_type='finance',
                input_data=json.dumps(stock_data),
                prediction_result=ml_result.get('prediction', 'UNKNOWN') if ml_result else 'UNKNOWN',
                confidence_score=ml_result.get('confidence') if ml_result else None,
                model_version='v1.0'
            )
            db.session.add(prediction)
            db.session.commit()
            
            # 7. Construct response aligned with frontend expectations
            response = {
                'asset': {
                    'ticker': ticker,
                    'name': stock_data.get('name', ticker),
                    'prices': stock_data.get('prices', []),
                    'indicators': stock_data.get('indicators', {})
                },
                'model_score': ml_score,
                'gpt_analysis': {
                    'domain': gpt_analysis.get('domain', 'finance'),
                    'summary': gpt_analysis.get('summary', 'Analyse non disponible'),
                    'analysis': gpt_analysis.get('analysis', 'Analyse détaillée non disponible'),
                    'prediction_type': gpt_analysis.get('prediction_type', 'trend'),
                    'prediction_value': gpt_analysis.get('prediction_value', 'NEUTRAL'),
                    'confidence': gpt_analysis.get('confidence', 0.0),
                    'caveats': gpt_analysis.get('caveats', 'Prédictions expérimentales'),
                    'educational_reminder': gpt_analysis.get('educational_reminder',
                        'Cette plateforme est strictement éducative. Ne pas utiliser pour des investissements réels.')
                }
            }
            
            return response, 200
            
        except Exception as e:
            logger.error(f"Error in finance prediction endpoint: {e}")
            db.session.rollback()
            return {
                'error': 'Internal server error',
                'details': str(e)
            }, 500


@api.route('/watchlist')
class Watchlist(Resource):
    """Manage user's stock watchlist."""
    
    @token_required
    @api.response(200, 'Success')
    def get(self, current_user):
        """Get user's watchlist (feature coming soon)."""
        return {
            'watchlist': [],
            'message': 'Fonctionnalité à venir'
        }, 200
    
    @token_required
    @api.expect(api.model('AddToWatchlist', {
        'symbol': fields.String(required=True, description='Stock symbol')
    }))
    def post(self, current_user):
        """Add stock to watchlist (feature coming soon)."""
        return {
            'message': 'Fonctionnalité à venir'
        }, 200
