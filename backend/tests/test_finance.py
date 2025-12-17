"""
Tests pour les endpoints finance.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestFinancePredict:
    """Tests pour l'endpoint /api/v1/finance/predict/<ticker>."""
    
    def test_predict_success(self, client, auth_headers):
        """Test prediction finance reussie."""
        response = client.get('/api/v1/finance/predict/AAPL', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'asset' in data
        assert 'model_score' in data
        assert 'gpt_analysis' in data
        assert 'disclaimer' in data
    
    def test_predict_asset_structure(self, client, auth_headers):
        """Test structure des donnees d'actif."""
        response = client.get('/api/v1/finance/predict/AAPL', headers=auth_headers)
        data = response.get_json()
        
        asset = data.get('asset', {})
        assert 'ticker' in asset
        assert 'name' in asset
        assert 'indicators' in asset
    
    def test_predict_gpt_analysis_structure(self, client, auth_headers):
        """Test structure de l'analyse GPT."""
        response = client.get('/api/v1/finance/predict/AAPL', headers=auth_headers)
        data = response.get_json()
        
        gpt = data.get('gpt_analysis', {})
        assert 'domain' in gpt
        assert gpt['domain'] == 'finance'
        assert 'summary' in gpt
        assert 'prediction_type' in gpt
        assert 'disclaimer' in gpt
    
    def test_predict_trend_value(self, client, auth_headers):
        """Test que la prediction de tendance est valide."""
        response = client.get('/api/v1/finance/predict/AAPL', headers=auth_headers)
        data = response.get_json()
        
        gpt = data.get('gpt_analysis', {})
        prediction_value = gpt.get('prediction_value')
        
        # La valeur devrait etre UP, DOWN, NEUTRAL ou un nombre
        valid_trends = ['UP', 'DOWN', 'NEUTRAL']
        is_valid = prediction_value in valid_trends or isinstance(prediction_value, (int, float))
        assert is_valid
    
    def test_predict_without_auth(self, client):
        """Test prediction sans authentification."""
        response = client.get('/api/v1/finance/predict/AAPL')
        
        assert response.status_code == 401
    
    def test_predict_different_tickers(self, client, auth_headers):
        """Test prediction pour differents tickers."""
        tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
        
        for ticker in tickers:
            response = client.get(f'/api/v1/finance/predict/{ticker}', headers=auth_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data['asset']['ticker'] == ticker
    
    def test_predict_lowercase_ticker(self, client, auth_headers):
        """Test que le ticker est converti en majuscules."""
        response = client.get('/api/v1/finance/predict/aapl', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['asset']['ticker'] == 'AAPL'
    
    def test_predict_with_period(self, client, auth_headers):
        """Test prediction avec periode specifiee."""
        response = client.get(
            '/api/v1/finance/predict/AAPL?period=3mo',
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    @patch('app.services.finance_api_service.finance_api_service.get_stock_data')
    def test_predict_api_error(self, mock_get_stock, client, auth_headers):
        """Test prediction quand l'API finance echoue."""
        mock_get_stock.return_value = None
        
        response = client.get('/api/v1/finance/predict/INVALID', headers=auth_headers)
        
        # Devrait retourner le mock par defaut ou 404
        assert response.status_code in [200, 404]


class TestFinanceStocks:
    """Tests pour l'endpoint /api/v1/finance/stocks."""
    
    def test_get_stocks_success(self, client, auth_headers):
        """Test recuperation des actifs."""
        response = client.get('/api/v1/finance/stocks', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'stocks' in data
        assert 'count' in data
        assert isinstance(data['stocks'], list)
    
    def test_get_stocks_with_limit(self, client, auth_headers):
        """Test recuperation des actifs avec limite."""
        response = client.get(
            '/api/v1/finance/stocks?limit=5',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['stocks']) <= 5
    
    def test_get_stocks_without_auth(self, client):
        """Test recuperation des actifs sans auth."""
        response = client.get('/api/v1/finance/stocks')
        
        assert response.status_code == 401


class TestFinancePredictionHistory:
    """Tests pour l'endpoint /api/v1/finance/predictions/history."""
    
    def test_get_history_empty(self, client, auth_headers):
        """Test historique vide."""
        response = client.get('/api/v1/finance/predictions/history', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'predictions' in data
        assert 'total' in data
    
    def test_get_history_after_prediction(self, client, auth_headers):
        """Test historique apres une prediction."""
        # Faire une prediction
        client.get('/api/v1/finance/predict/AAPL', headers=auth_headers)
        
        # Verifier l'historique
        response = client.get('/api/v1/finance/predictions/history', headers=auth_headers)
        data = response.get_json()
        
        assert data['total'] >= 1
    
    def test_get_history_pagination(self, client, auth_headers):
        """Test pagination de l'historique."""
        response = client.get(
            '/api/v1/finance/predictions/history?limit=5&offset=0',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'limit' in data
        assert 'offset' in data
