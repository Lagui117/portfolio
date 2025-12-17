"""
Tests pour le service API finance.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestFinanceAPIService:
    """Tests pour le service API finance."""
    
    def test_service_import(self):
        """Test import du service."""
        from app.services.finance_api_service import finance_api_service
        assert finance_api_service is not None
    
    def test_get_stock_data_mock(self, app):
        """Test recuperation de donnees stock en mode mock."""
        with app.app_context():
            from app.services.finance_api_service import FinanceAPIService
            
            service = FinanceAPIService()
            service.use_mock = True
            
            result = service.get_stock_data('AAPL')
            
            assert result is not None
            assert 'symbol' in result
            assert 'name' in result
            assert 'indicators' in result
    
    def test_get_stock_data_known_tickers(self, app):
        """Test recuperation pour tickers connus."""
        with app.app_context():
            from app.services.finance_api_service import FinanceAPIService
            
            service = FinanceAPIService()
            service.use_mock = True
            
            tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
            for ticker in tickers:
                result = service.get_stock_data(ticker)
                assert result is not None
                assert result['symbol'] == ticker
    
    def test_get_stock_data_unknown_ticker(self, app):
        """Test recuperation pour ticker inconnu (genere donnees mock)."""
        with app.app_context():
            from app.services.finance_api_service import FinanceAPIService
            
            service = FinanceAPIService()
            service.use_mock = True
            
            result = service.get_stock_data('UNKNOWN')
            
            assert result is not None
            assert result['symbol'] == 'UNKNOWN'
    
    def test_stock_data_structure(self, app):
        """Test structure des donnees de stock."""
        with app.app_context():
            from app.services.finance_api_service import FinanceAPIService
            
            service = FinanceAPIService()
            service.use_mock = True
            
            result = service.get_stock_data('AAPL')
            
            required_fields = ['symbol', 'name', 'current_price', 'indicators', 'prices']
            for field in required_fields:
                assert field in result
            
            # Verifier structure indicateurs
            indicators = result['indicators']
            assert 'RSI' in indicators
            assert 'MA_5' in indicators
    
    def test_get_stock_data_case_insensitive(self, app):
        """Test que le ticker est converti en majuscules."""
        with app.app_context():
            from app.services.finance_api_service import FinanceAPIService
            
            service = FinanceAPIService()
            service.use_mock = True
            
            result = service.get_stock_data('aapl')
            
            assert result['symbol'] == 'AAPL'
    
    def test_get_popular_stocks(self, app):
        """Test recuperation des actifs populaires."""
        with app.app_context():
            from app.services.finance_api_service import FinanceAPIService
            
            service = FinanceAPIService()
            
            result = service.get_popular_stocks(limit=5)
            
            assert isinstance(result, list)
            assert len(result) <= 5
            
            for stock in result:
                assert 'ticker' in stock
                assert 'name' in stock
    
    def test_get_popular_stocks_by_sector(self, app):
        """Test recuperation par secteur."""
        with app.app_context():
            from app.services.finance_api_service import FinanceAPIService
            
            service = FinanceAPIService()
            
            result = service.get_popular_stocks(sector='Technology')
            
            for stock in result:
                assert stock['sector'] == 'Technology'
    
    def test_prices_structure(self, app):
        """Test structure des prix historiques."""
        with app.app_context():
            from app.services.finance_api_service import FinanceAPIService
            
            service = FinanceAPIService()
            service.use_mock = True
            
            result = service.get_stock_data('AAPL', '1mo')
            
            prices = result.get('prices', [])
            assert isinstance(prices, list)
            
            if prices:
                price_entry = prices[0]
                required_fields = ['date', 'open', 'high', 'low', 'close', 'volume']
                for field in required_fields:
                    assert field in price_entry
    
    def test_indicators_values(self, app):
        """Test que les indicateurs ont des valeurs valides."""
        with app.app_context():
            from app.services.finance_api_service import FinanceAPIService
            
            service = FinanceAPIService()
            service.use_mock = True
            
            result = service.get_stock_data('AAPL')
            indicators = result.get('indicators', {})
            
            # RSI devrait etre entre 0 et 100
            rsi = indicators.get('RSI')
            if rsi is not None:
                assert 0 <= rsi <= 100
            
            # Volatilite devrait etre positive
            volatility = indicators.get('volatility_daily')
            if volatility is not None:
                assert volatility >= 0
