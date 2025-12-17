"""
Tests pour les endpoints d'analyse financiere.
- GET /api/v1/finance/predict/<ticker>
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestFinancePredictEndpoint:
    """Tests pour l'endpoint de prediction financiere."""
    
    @patch('app.api.v1.finance.finance_api_service')
    @patch('app.api.v1.finance.prediction_service')
    @patch('app.api.v1.finance.gpt_service')
    def test_predict_stock_success(
        self,
        mock_gpt,
        mock_prediction,
        mock_finance_api,
        client,
        auth_headers,
        sample_stock_data
    ):
        """Prediction reussie pour un ticker valide."""
        # Configuration des mocks
        mock_finance_api.get_stock_data.return_value = sample_stock_data
        mock_prediction.predict_stock.return_value = 'UP'
        mock_gpt.analyse_finance.return_value = {
            'domain': 'finance',
            'summary': 'AAPL montre une tendance haussiere',
            'analysis': 'Indicateurs techniques positifs...',
            'prediction_type': 'trend',
            'prediction_value': 'UP',
            'confidence': 0.65,
            'caveats': 'Volatilite du marche...',
            'disclaimer': 'Analyse a titre informatif uniquement.'
        }
        
        response = client.get(
            '/api/v1/finance/predict/AAPL',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        json_data = response.get_json()
        
        assert 'asset' in json_data
        assert 'model_score' in json_data
        assert 'gpt_analysis' in json_data
        
        assert json_data['gpt_analysis']['domain'] == 'finance'
        assert json_data['gpt_analysis']['prediction_value'] == 'UP'
        
        # Verifier les appels
        mock_finance_api.get_stock_data.assert_called_once_with('AAPL', '1mo')
        mock_prediction.predict_stock.assert_called_once_with(sample_stock_data)
        mock_gpt.analyse_finance.assert_called_once()
    
    @patch('app.api.v1.finance.finance_api_service')
    @patch('app.api.v1.finance.prediction_service')
    @patch('app.api.v1.finance.gpt_service')
    def test_predict_stock_with_custom_period(
        self,
        mock_gpt,
        mock_prediction,
        mock_finance_api,
        client,
        auth_headers,
        sample_stock_data
    ):
        """Prediction avec periode personnalisee."""
        mock_finance_api.get_stock_data.return_value = sample_stock_data
        mock_prediction.predict_stock.return_value = 'NEUTRAL'
        mock_gpt.analyse_finance.return_value = {
            'domain': 'finance',
            'summary': 'Tendance neutre',
            'analysis': 'Marche stable',
            'prediction_type': 'trend',
            'prediction_value': 'NEUTRAL',
            'confidence': 0.50,
            'caveats': 'Incertitude elevee',
            'disclaimer': 'Analyse a titre informatif.'
        }
        
        response = client.get(
            '/api/v1/finance/predict/TSLA?period=3mo',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verifier que le parametre period a ete passe
        mock_finance_api.get_stock_data.assert_called_once_with('TSLA', '3mo')
    
    @patch('app.api.v1.finance.finance_api_service')
    def test_predict_stock_not_found(
        self,
        mock_finance_api,
        client,
        auth_headers
    ):
        """Ticker non trouve - erreur 404."""
        mock_finance_api.get_stock_data.return_value = None
        
        response = client.get(
            '/api/v1/finance/predict/INVALID',
            headers=auth_headers
        )
        
        assert response.status_code == 404
        json_data = response.get_json()
        
        assert 'error' in json_data
        # Le message peut être "non trouve" ou "aucune donnee"
        assert ('non trouve' in json_data['message'].lower() or 'aucune donnee' in json_data['message'].lower())
    
    @patch('app.api.v1.finance.finance_api_service')
    @patch('app.api.v1.finance.prediction_service')
    def test_predict_stock_prediction_error(
        self,
        mock_prediction,
        mock_finance_api,
        client,
        auth_headers,
        sample_stock_data
    ):
        """Erreur lors de la prediction."""
        mock_finance_api.get_stock_data.return_value = sample_stock_data
        mock_prediction.predict_stock.side_effect = Exception('Model error')
        
        response = client.get(
            '/api/v1/finance/predict/AAPL',
            headers=auth_headers
        )
        
        assert response.status_code == 500
    
    def test_predict_stock_requires_auth(self, client):
        """Acces refuse sans authentification."""
        response = client.get('/api/v1/finance/predict/AAPL')
        
        assert response.status_code == 401
    
    def test_predict_stock_lowercase_ticker(
        self,
        client,
        auth_headers
    ):
        """Le ticker en minuscules est converti en majuscules."""
        with patch('app.api.v1.finance.finance_api_service') as mock_api, \
             patch('app.api.v1.finance.prediction_service') as mock_pred, \
             patch('app.api.v1.finance.gpt_service') as mock_gpt:
            
            mock_api.get_stock_data.return_value = {'symbol': 'AAPL'}
            mock_pred.predict_stock.return_value = 'UP'
            mock_gpt.analyse_finance.return_value = {
                'domain': 'finance',
                'summary': 'Test',
                'analysis': 'Test',
                'prediction_type': 'trend',
                'prediction_value': 'UP',
                'confidence': 0.6,
                'caveats': 'Test',
                'disclaimer': 'Test'
            }
            
            response = client.get(
                '/api/v1/finance/predict/aapl',
                headers=auth_headers
            )
            
            # Le ticker doit etre converti en majuscules
            mock_api.get_stock_data.assert_called_with('AAPL', '1mo')
