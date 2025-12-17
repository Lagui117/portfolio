"""
Tests pour le service API finance (mode mock).
"""

import pytest
from unittest.mock import patch, Mock


class TestFinanceApiService:
    """Tests pour finance_api_service."""
    
    def test_get_stock_data_success_mock_mode(self):
        """Recuperation reussie des donnees financieres en mode mock."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        result = service.get_stock_data('AAPL', '1mo')
        
        assert result is not None
        assert 'symbol' in result
        assert result['symbol'] == 'AAPL'
        assert 'current_price' in result
    
    def test_get_stock_data_invalid_ticker(self):
        """Ticker invalide retourne des données mock."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        
        # En mode mock, tous les tickers retournent des données génériques
        result = service.get_stock_data('INVALIDTICKER123', '1mo')
        
        # Le mode mock retourne toujours quelque chose
        assert result is not None
        assert 'symbol' in result
    
    def test_get_stock_data_with_different_periods(self):
        """Test avec differentes periodes."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        
        for period in ['1d', '1mo', '3mo', '1y']:
            result = service.get_stock_data('AAPL', period)
            assert result is not None
            assert 'symbol' in result
    
    def test_get_stock_data_different_tickers(self):
        """Test avec differents tickers disponibles en mock."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        
        for ticker in ['AAPL', 'GOOGL', 'MSFT', 'TSLA']:
            result = service.get_stock_data(ticker, '1mo')
            assert result is not None
            assert result['symbol'] == ticker
