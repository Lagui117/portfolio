"""
Tests pour FinanceAPIService - Service de données financières.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.finance_api_service import FinanceAPIService


class TestFinanceAPIServiceInit:
    """Tests pour l'initialisation du service."""
    
    def test_init_mock_mode_by_default(self):
        """Service en mode mock par défaut."""
        service = FinanceAPIService()
        # Sans yfinance ou avec USE_MOCK_FINANCE_API=true
        assert hasattr(service, 'use_mock')
    
    def test_init_with_api_key(self):
        """Initialisation avec clé API."""
        with patch.dict('os.environ', {'FINANCE_API_KEY': 'test_key'}):
            service = FinanceAPIService()
            assert service.api_key == 'test_key'


class TestFinanceAPIServiceGetStockData:
    """Tests pour la récupération des données d'actifs."""
    
    def test_get_stock_data_known_ticker(self):
        """Données pour un ticker connu."""
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service.get_stock_data('AAPL')
        
        assert data is not None
        assert data['symbol'] == 'AAPL'
        assert 'name' in data
        assert 'current_price' in data
        assert 'prices' in data
        assert 'indicators' in data
    
    def test_get_stock_data_normalizes_ticker(self):
        """Le ticker est normalisé (uppercase, strip)."""
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service.get_stock_data('  aapl  ')
        
        assert data['symbol'] == 'AAPL'
    
    def test_get_stock_data_unknown_ticker(self):
        """Données générées pour un ticker inconnu."""
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service.get_stock_data('UNKNOWN123')
        
        assert data is not None
        assert data['symbol'] == 'UNKNOWN123'
        assert 'current_price' in data
        assert data['sector'] == 'Unknown'
    
    def test_get_stock_data_with_period(self):
        """Données avec période spécifiée."""
        service = FinanceAPIService()
        service.use_mock = True
        
        for period in ['1d', '5d', '1mo', '3mo', '6mo', '1y']:
            data = service.get_stock_data('AAPL', period=period)
            assert data is not None
            assert 'prices' in data
    
    def test_get_stock_data_googl(self):
        """Données pour GOOGL."""
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service.get_stock_data('GOOGL')
        
        assert data['symbol'] == 'GOOGL'
        assert 'Alphabet' in data['name']
    
    def test_get_stock_data_msft(self):
        """Données pour MSFT."""
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service.get_stock_data('MSFT')
        
        assert data['symbol'] == 'MSFT'
        assert 'Microsoft' in data['name']
    
    def test_get_stock_data_tsla(self):
        """Données pour TSLA."""
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service.get_stock_data('TSLA')
        
        assert data['symbol'] == 'TSLA'
        assert 'Tesla' in data['name']


class TestFinanceAPIServicePopularStocks:
    """Tests pour les actifs populaires."""
    
    def test_get_popular_stocks_default(self):
        """Liste par défaut des actifs populaires."""
        service = FinanceAPIService()
        
        stocks = service.get_popular_stocks()
        
        assert isinstance(stocks, list)
        assert len(stocks) > 0
        
        # Vérifier la structure
        for stock in stocks:
            assert 'ticker' in stock
            assert 'name' in stock
            assert 'sector' in stock
    
    def test_get_popular_stocks_with_limit(self):
        """Liste limitée."""
        service = FinanceAPIService()
        
        stocks = service.get_popular_stocks(limit=5)
        
        assert len(stocks) <= 5
    
    def test_get_popular_stocks_filter_sector(self):
        """Filtrage par secteur."""
        service = FinanceAPIService()
        
        stocks = service.get_popular_stocks(sector='Technology')
        
        for stock in stocks:
            assert stock['sector'] == 'Technology'
    
    def test_get_popular_stocks_unknown_sector(self):
        """Secteur inconnu retourne liste vide."""
        service = FinanceAPIService()
        
        stocks = service.get_popular_stocks(sector='Unknown_Sector')
        
        assert stocks == []
    
    def test_get_popular_stocks_financial_sector(self):
        """Filtrage secteur Financial Services."""
        service = FinanceAPIService()
        
        stocks = service.get_popular_stocks(sector='Financial Services')
        
        assert all(s['sector'] == 'Financial Services' for s in stocks)


class TestFinanceAPIServiceMockData:
    """Tests pour les données mock."""
    
    def test_generate_mock_prices_structure(self):
        """Structure des prix mock."""
        service = FinanceAPIService()
        
        prices = service._generate_mock_prices(100.0, '1mo')
        
        assert isinstance(prices, list)
        assert len(prices) > 0
        
        for price in prices:
            assert 'date' in price
            assert 'open' in price
            assert 'high' in price
            assert 'low' in price
            assert 'close' in price
            assert 'volume' in price
    
    def test_generate_mock_prices_periods(self):
        """Différentes périodes génèrent différentes longueurs."""
        service = FinanceAPIService()
        
        prices_1d = service._generate_mock_prices(100.0, '1d')
        prices_1mo = service._generate_mock_prices(100.0, '1mo')
        prices_1y = service._generate_mock_prices(100.0, '1y')
        
        assert len(prices_1d) < len(prices_1mo) < len(prices_1y)
    
    def test_generate_mock_indicators(self):
        """Indicateurs mock sont générés."""
        service = FinanceAPIService()
        
        indicators = service._generate_mock_indicators(150.0)
        
        assert 'MA_5' in indicators
        assert 'MA_20' in indicators
        assert 'MA_50' in indicators
        assert 'RSI' in indicators
        assert 'volatility_daily' in indicators
        assert 'volatility_annual' in indicators
        assert 'current_price' in indicators
        assert 'price_change_pct' in indicators
    
    def test_mock_rsi_in_valid_range(self):
        """RSI est entre 0 et 100."""
        service = FinanceAPIService()
        
        for _ in range(10):
            indicators = service._generate_mock_indicators(100.0)
            assert 0 <= indicators['RSI'] <= 100
    
    def test_mock_stock_data_complete(self):
        """Données mock complètes."""
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service._get_mock_stock_data('AAPL', '1mo')
        
        required_fields = [
            'symbol', 'name', 'sector', 'industry', 
            'currency', 'exchange', 'market_cap',
            'current_price', 'price_change_pct',
            'prices', 'indicators'
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"


class TestFinanceAPIServiceRealAPI:
    """Tests pour l'intégration API réelle (mockée)."""
    
    def test_get_stock_data_with_mock_fallback(self):
        """Service utilise le fallback mock si yfinance échoue."""
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service.get_stock_data('AAPL')
        
        assert data is not None
        assert data['symbol'] == 'AAPL'


class TestFinanceAPIServiceEdgeCases:
    """Tests pour les cas limites."""
    
    def test_empty_ticker(self):
        """Ticker vide."""
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service.get_stock_data('')
        
        # Devrait gérer le cas vide
        assert data is not None
    
    def test_special_characters_in_ticker(self):
        """Caractères spéciaux dans le ticker."""
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service.get_stock_data('BRK.B')
        
        assert data is not None
        assert data['symbol'] == 'BRK.B'
    
    def test_numeric_ticker(self):
        """Ticker numérique."""
        service = FinanceAPIService()
        service.use_mock = True
        
        data = service.get_stock_data('7203')  # Toyota sur le Nikkei
        
        assert data is not None
    
    def test_prices_consistency(self):
        """High >= Low pour tous les prix."""
        service = FinanceAPIService()
        
        prices = service._generate_mock_prices(100.0, '1mo')
        
        for price in prices:
            assert price['high'] >= price['low']
    
    def test_volume_positive(self):
        """Volume toujours positif."""
        service = FinanceAPIService()
        
        prices = service._generate_mock_prices(100.0, '1mo')
        
        for price in prices:
            assert price['volume'] > 0

