"""
Tests supplémentaires pour FinanceAPIService.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime


class TestFinanceAPIServiceInit:
    """Tests pour l'initialisation du service."""
    
    def test_import_service(self):
        """Tester l'import du service."""
        from app.services.finance_api_service import FinanceAPIService
        assert FinanceAPIService is not None
    
    def test_create_instance(self):
        """Créer une instance."""
        from app.services.finance_api_service import FinanceAPIService
        service = FinanceAPIService()
        assert service is not None
    
    def test_has_use_mock_attribute(self):
        """L'instance a un attribut use_mock."""
        from app.services.finance_api_service import FinanceAPIService
        service = FinanceAPIService()
        assert hasattr(service, 'use_mock')
    
    def test_has_api_key_attribute(self):
        """L'instance a un attribut api_key."""
        from app.services.finance_api_service import FinanceAPIService
        service = FinanceAPIService()
        assert hasattr(service, 'api_key')


class TestFinanceAPIServiceMockData:
    """Tests pour les données mock."""
    
    def test_get_mock_stock_data_known_ticker(self):
        """Données mock pour un ticker connu."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service._get_mock_stock_data('AAPL', '1mo')
        
        assert data is not None
        assert data['symbol'] == 'AAPL'
        assert data['name'] == 'Apple Inc.'
        assert 'prices' in data
        assert 'indicators' in data
    
    def test_get_mock_stock_data_googl(self):
        """Données mock pour GOOGL."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service._get_mock_stock_data('GOOGL', '1mo')
        
        assert data is not None
        assert data['symbol'] == 'GOOGL'
        assert data['sector'] == 'Technology'
    
    def test_get_mock_stock_data_msft(self):
        """Données mock pour MSFT."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service._get_mock_stock_data('MSFT', '1mo')
        
        assert data is not None
        assert data['symbol'] == 'MSFT'
    
    def test_get_mock_stock_data_tsla(self):
        """Données mock pour TSLA."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service._get_mock_stock_data('TSLA', '1mo')
        
        assert data is not None
        assert data['symbol'] == 'TSLA'
        assert data['sector'] == 'Consumer Cyclical'
    
    def test_get_mock_stock_data_unknown_ticker(self):
        """Données mock pour un ticker inconnu."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service._get_mock_stock_data('UNKNOWN', '1mo')
        
        assert data is not None
        assert data['symbol'] == 'UNKNOWN'
        assert data['sector'] == 'Unknown'


class TestFinanceAPIServiceGetStockData:
    """Tests pour get_stock_data."""
    
    def test_get_stock_data_mock_mode(self):
        """get_stock_data en mode mock."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service.get_stock_data('AAPL')
        
        assert data is not None
        assert data['symbol'] == 'AAPL'
    
    def test_get_stock_data_normalizes_ticker(self):
        """get_stock_data normalise le ticker."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        service.use_mock = True
        
        # Ticker en minuscules avec espaces
        data = service.get_stock_data('  aapl  ')
        
        assert data['symbol'] == 'AAPL'
    
    def test_get_stock_data_different_periods(self):
        """get_stock_data avec différentes périodes."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        service.use_mock = True
        
        for period in ['1d', '5d', '1mo', '3mo', '6mo', '1y']:
            data = service.get_stock_data('AAPL', period=period)
            assert data is not None


class TestFinanceAPIServicePopularStocks:
    """Tests pour get_popular_stocks."""
    
    def test_get_popular_stocks(self):
        """Récupérer les actions populaires."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        stocks = service.get_popular_stocks()
        
        assert isinstance(stocks, list)
        assert len(stocks) > 0
    
    def test_get_popular_stocks_with_limit(self):
        """Récupérer avec une limite."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        stocks = service.get_popular_stocks(limit=5)
        
        assert len(stocks) <= 5
    
    def test_get_popular_stocks_filter_by_sector(self):
        """Filtrer par secteur."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        stocks = service.get_popular_stocks(sector='Technology')
        
        for stock in stocks:
            assert stock['sector'] == 'Technology'
    
    def test_get_popular_stocks_filter_financial(self):
        """Filtrer par secteur Financial Services."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        stocks = service.get_popular_stocks(sector='Financial Services')
        
        # Tous les résultats doivent être du secteur financier
        for stock in stocks:
            assert stock['sector'] == 'Financial Services'


class TestFinanceAPIServiceMockGenerators:
    """Tests pour les générateurs mock."""
    
    def test_generate_mock_prices(self):
        """Génère des prix historiques mock."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        prices = service._generate_mock_prices(150.0, '1mo')
        
        assert isinstance(prices, list)
        assert len(prices) > 0
        
        # Vérifier la structure
        for price in prices:
            assert 'date' in price
            assert 'open' in price
            assert 'high' in price
            assert 'low' in price
            assert 'close' in price
            assert 'volume' in price
    
    def test_generate_mock_prices_different_periods(self):
        """Génère des prix pour différentes périodes."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        
        days_expected = {'1d': 1, '5d': 5, '1mo': 22, '3mo': 66}
        
        for period, expected_days in days_expected.items():
            prices = service._generate_mock_prices(100.0, period)
            assert len(prices) == expected_days
    
    def test_generate_mock_indicators(self):
        """Génère des indicateurs techniques mock."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        indicators = service._generate_mock_indicators(150.0)
        
        assert isinstance(indicators, dict)
        assert 'MA_5' in indicators
        assert 'MA_20' in indicators
        assert 'RSI' in indicators
        assert 'volatility_daily' in indicators
        assert 'current_price' in indicators
        assert indicators['current_price'] == 150.0


class TestFinanceAPIServiceGlobalInstance:
    """Tests pour l'instance globale."""
    
    def test_global_instance_exists(self):
        """L'instance globale existe."""
        from app.services.finance_api_service import finance_api_service
        assert finance_api_service is not None
    
    def test_global_instance_is_correct_type(self):
        """L'instance globale est du bon type."""
        from app.services.finance_api_service import finance_api_service, FinanceAPIService
        assert isinstance(finance_api_service, FinanceAPIService)


class TestFinanceAPIServiceCalculateIndicators:
    """Tests pour _calculate_indicators avec des DataFrames réels."""
    
    def test_calculate_indicators_short_history(self):
        """Calcul avec un historique court."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        
        # DataFrame court (3 jours)
        dates = pd.date_range(start='2024-01-01', periods=3, freq='D')
        hist = pd.DataFrame({
            'Open': [100.0, 101.0, 102.0],
            'High': [102.0, 103.0, 104.0],
            'Low': [99.0, 100.0, 101.0],
            'Close': [101.0, 102.0, 103.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=dates)
        
        indicators = service._calculate_indicators(hist)
        
        assert 'current_price' in indicators
        assert indicators['current_price'] == 103.0
    
    def test_calculate_indicators_medium_history(self):
        """Calcul avec un historique moyen (20 jours)."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        
        # DataFrame 20 jours
        dates = pd.date_range(start='2024-01-01', periods=20, freq='D')
        close_prices = [100 + i * 0.5 + np.random.uniform(-1, 1) for i in range(20)]
        
        hist = pd.DataFrame({
            'Open': [p - 0.5 for p in close_prices],
            'High': [p + 1 for p in close_prices],
            'Low': [p - 1 for p in close_prices],
            'Close': close_prices,
            'Volume': [1000000 + i * 10000 for i in range(20)]
        }, index=dates)
        
        indicators = service._calculate_indicators(hist)
        
        assert 'MA_5' in indicators
        assert 'MA_20' in indicators
        assert 'RSI' in indicators
        assert 'volatility_daily' in indicators
    
    def test_calculate_indicators_long_history(self):
        """Calcul avec un historique long (50+ jours)."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        
        # DataFrame 60 jours
        dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
        close_prices = [100 + i * 0.3 + np.random.uniform(-2, 2) for i in range(60)]
        
        hist = pd.DataFrame({
            'Open': [p - 0.5 for p in close_prices],
            'High': [p + 1 for p in close_prices],
            'Low': [p - 1 for p in close_prices],
            'Close': close_prices,
            'Volume': [1000000 + i * 5000 for i in range(60)]
        }, index=dates)
        
        indicators = service._calculate_indicators(hist)
        
        assert 'MA_5' in indicators
        assert 'MA_20' in indicators
        assert 'MA_50' in indicators
        assert 'RSI' in indicators
        assert 'volatility_annual' in indicators
    
    def test_calculate_indicators_rsi_zero_loss(self):
        """Calcul RSI quand il n'y a pas de pertes (price always up)."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        
        # Prix toujours en hausse
        dates = pd.date_range(start='2024-01-01', periods=20, freq='D')
        close_prices = [100 + i for i in range(20)]  # Toujours en hausse
        
        hist = pd.DataFrame({
            'Open': [p - 0.5 for p in close_prices],
            'High': [p + 1 for p in close_prices],
            'Low': [p - 0.2 for p in close_prices],
            'Close': close_prices,
            'Volume': [1000000] * 20
        }, index=dates)
        
        indicators = service._calculate_indicators(hist)
        
        assert 'RSI' in indicators
        assert indicators['RSI'] == 100.0


class TestFinanceAPIServiceFormatStockData:
    """Tests pour _format_stock_data."""
    
    def test_format_stock_data_basic(self):
        """Formatage de base des données stock."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        
        # Préparer les données
        ticker = 'AAPL'
        info = {
            'longName': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'currency': 'USD',
            'exchange': 'NASDAQ',
            'marketCap': 2800000000000
        }
        
        dates = pd.date_range(start='2024-01-01', periods=5, freq='D')
        hist = pd.DataFrame({
            'Open': [150.0, 151.0, 152.0, 153.0, 154.0],
            'High': [152.0, 153.0, 154.0, 155.0, 156.0],
            'Low': [149.0, 150.0, 151.0, 152.0, 153.0],
            'Close': [151.0, 152.0, 153.0, 154.0, 155.0],
            'Volume': [1000000, 1100000, 1200000, 1300000, 1400000]
        }, index=dates)
        
        indicators = {'current_price': 155.0, 'price_change_pct': 1.5}
        
        result = service._format_stock_data(ticker, info, hist, indicators)
        
        assert result['symbol'] == 'AAPL'
        assert result['name'] == 'Apple Inc.'
        assert result['sector'] == 'Technology'
        assert len(result['prices']) == 5
    
    def test_format_stock_data_missing_info(self):
        """Formatage avec infos manquantes."""
        from app.services.finance_api_service import FinanceAPIService
        
        service = FinanceAPIService()
        
        ticker = 'TEST'
        info = {}  # Pas d'infos
        
        dates = pd.date_range(start='2024-01-01', periods=3, freq='D')
        hist = pd.DataFrame({
            'Open': [100.0, 101.0, 102.0],
            'High': [102.0, 103.0, 104.0],
            'Low': [99.0, 100.0, 101.0],
            'Close': [101.0, 102.0, 103.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=dates)
        
        indicators = {'current_price': 103.0}
        
        result = service._format_stock_data(ticker, info, hist, indicators)
        
        assert result['symbol'] == 'TEST'
        assert result['name'] == 'TEST'  # Fallback au ticker
        assert result['sector'] == 'Unknown'

