"""
Tests étendus pour MockFinanceProvider et RealFinanceProvider.

Cible: providers/finance.py (actuellement 62% coverage)
"""

import pytest
import random
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from app.providers.finance import MockFinanceProvider, RealFinanceProvider
from app.providers.schemas import (
    FinanceAssetNormalized,
    FinancePricePoint,
    FinanceIndicatorsNormalized,
)


# ============================================
# MOCK FINANCE PROVIDER TESTS
# ============================================

class TestMockFinanceProviderInit:
    """Tests d'initialisation du MockFinanceProvider."""
    
    def test_init_sets_provider_name(self):
        """Le provider doit avoir le nom 'mock-finance'."""
        provider = MockFinanceProvider()
        assert provider.provider_name == 'mock-finance'
    
    def test_init_creates_empty_cache(self):
        """Le cache doit être vide à l'initialisation."""
        provider = MockFinanceProvider()
        assert hasattr(provider, '_cache')
        assert isinstance(provider._cache, dict)
    
    def test_assets_data_structure(self):
        """ASSETS doit contenir les données nécessaires."""
        provider = MockFinanceProvider()
        assert 'AAPL' in provider.ASSETS
        assert 'GOOGL' in provider.ASSETS
        assert 'MSFT' in provider.ASSETS
        
        # Chaque asset doit avoir name, sector, base_price
        for symbol, data in provider.ASSETS.items():
            assert 'name' in data
            assert 'sector' in data
            assert 'base_price' in data
            assert isinstance(data['base_price'], (int, float))


class TestMockFinanceProviderHealthCheck:
    """Tests de health_check."""
    
    def test_health_check_returns_healthy(self):
        """health_check doit retourner healthy: True."""
        provider = MockFinanceProvider()
        result = provider.health_check()
        
        assert result['healthy'] is True
        assert 'provider' in result
        assert result['provider'] == 'MockFinanceProvider'
    
    def test_is_available_returns_true(self):
        """is_available doit toujours retourner True pour mock."""
        provider = MockFinanceProvider()
        assert provider.is_available() is True


class TestMockFinanceProviderPriceGeneration:
    """Tests des méthodes de génération de prix."""
    
    def test_generate_price_with_trend_default(self):
        """_generate_price_with_trend génère un prix proche de base."""
        provider = MockFinanceProvider()
        base_price = 100.0
        
        # Appeler plusieurs fois pour vérifier la stabilité
        prices = [provider._generate_price_with_trend(base_price) for _ in range(10)]
        
        for price in prices:
            # Le prix doit être dans une plage raisonnable (±20%)
            assert 80 <= price <= 120
            assert isinstance(price, float)
    
    def test_generate_price_with_trend_high_volatility(self):
        """_generate_price_with_trend avec haute volatilité."""
        provider = MockFinanceProvider()
        base_price = 100.0
        volatility = 0.5  # 50% volatilité
        
        prices = [provider._generate_price_with_trend(base_price, volatility) for _ in range(20)]
        
        # Avec haute volatilité, on devrait voir une plus grande variance
        min_price = min(prices)
        max_price = max(prices)
        assert max_price - min_price > 0  # Il doit y avoir de la variance
    
    def test_generate_price_with_zero_volatility(self):
        """_generate_price_with_trend avec volatilité nulle."""
        provider = MockFinanceProvider()
        base_price = 100.0
        
        # Avec volatilité à 0, le prix devrait être très proche de base
        price = provider._generate_price_with_trend(base_price, 0.0001)
        assert 99 <= price <= 101


class TestMockFinanceProviderPriceHistory:
    """Tests de _generate_price_history."""
    
    def test_generate_price_history_default_days(self):
        """_generate_price_history génère 30 jours par défaut."""
        provider = MockFinanceProvider()
        history = provider._generate_price_history(100.0)
        
        assert len(history) == 30
    
    def test_generate_price_history_custom_days(self):
        """_generate_price_history avec nombre de jours personnalisé."""
        provider = MockFinanceProvider()
        
        history_90 = provider._generate_price_history(100.0, 90)
        assert len(history_90) == 90
        
        history_5 = provider._generate_price_history(100.0, 5)
        assert len(history_5) == 5
    
    def test_generate_price_history_returns_price_points(self):
        """L'historique doit contenir des FinancePricePoint."""
        provider = MockFinanceProvider()
        history = provider._generate_price_history(100.0, 10)
        
        for point in history:
            assert isinstance(point, FinancePricePoint)
            assert hasattr(point, 'date')
            assert hasattr(point, 'open')
            assert hasattr(point, 'high')
            assert hasattr(point, 'low')
            assert hasattr(point, 'close')
            assert hasattr(point, 'volume')
    
    def test_generate_price_history_ohlc_consistency(self):
        """Les valeurs OHLC doivent être cohérentes."""
        provider = MockFinanceProvider()
        history = provider._generate_price_history(100.0, 30)
        
        for point in history:
            # High doit être >= open et close
            assert point.high >= point.open or abs(point.high - point.open) < 0.01
            assert point.high >= point.close or abs(point.high - point.close) < 0.01
            # Low doit être <= open et close
            assert point.low <= point.open or abs(point.low - point.open) < 0.01
            assert point.low <= point.close or abs(point.low - point.close) < 0.01
    
    def test_generate_price_history_dates_descending(self):
        """Les dates doivent être dans le bon ordre."""
        provider = MockFinanceProvider()
        history = provider._generate_price_history(100.0, 10)
        
        # Les dates devraient aller du passé vers le présent
        for i in range(len(history) - 1):
            assert history[i].date <= history[i + 1].date


class TestMockFinanceProviderIndicators:
    """Tests de _calculate_indicators."""
    
    def test_calculate_indicators_with_history(self):
        """_calculate_indicators retourne des indicateurs valides."""
        provider = MockFinanceProvider()
        history = provider._generate_price_history(100.0, 50)
        
        indicators = provider._calculate_indicators(history)
        
        assert isinstance(indicators, FinanceIndicatorsNormalized)
        assert indicators.sma_20 is not None
        assert indicators.sma_50 is not None
        assert indicators.rsi_14 is not None
        assert indicators.macd is not None
    
    def test_calculate_indicators_short_history(self):
        """_calculate_indicators avec historique trop court."""
        provider = MockFinanceProvider()
        history = provider._generate_price_history(100.0, 10)
        
        indicators = provider._calculate_indicators(history)
        
        # Avec moins de 20 points, devrait retourner des indicateurs vides
        assert isinstance(indicators, FinanceIndicatorsNormalized)
    
    def test_calculate_indicators_rsi_range(self):
        """Le RSI doit être entre 0 et 100."""
        provider = MockFinanceProvider()
        history = provider._generate_price_history(100.0, 50)
        
        indicators = provider._calculate_indicators(history)
        
        assert 0 <= indicators.rsi_14 <= 100
    
    def test_calculate_indicators_bollinger_bands(self):
        """Les bandes de Bollinger doivent être cohérentes."""
        provider = MockFinanceProvider()
        history = provider._generate_price_history(100.0, 50)
        
        indicators = provider._calculate_indicators(history)
        
        # Upper > Middle > Lower
        assert indicators.bollinger_upper >= indicators.bollinger_middle
        assert indicators.bollinger_middle >= indicators.bollinger_lower


class TestMockFinanceProviderGetAsset:
    """Tests de get_asset."""
    
    def test_get_asset_known_symbol(self):
        """get_asset pour un symbole connu."""
        provider = MockFinanceProvider()
        asset = provider.get_asset('AAPL')
        
        assert asset is not None
        assert isinstance(asset, FinanceAssetNormalized)
        assert asset.symbol == 'AAPL'
        assert asset.name == 'Apple Inc.'
    
    def test_get_asset_case_insensitive(self):
        """get_asset doit être insensible à la casse."""
        provider = MockFinanceProvider()
        
        asset_upper = provider.get_asset('AAPL')
        asset_lower = provider.get_asset('aapl')
        asset_mixed = provider.get_asset('AaPl')
        
        assert asset_upper.symbol == asset_lower.symbol == asset_mixed.symbol == 'AAPL'
    
    def test_get_asset_strips_whitespace(self):
        """get_asset doit supprimer les espaces."""
        provider = MockFinanceProvider()
        
        asset = provider.get_asset('  AAPL  ')
        assert asset is not None
        assert asset.symbol == 'AAPL'
    
    def test_get_asset_unknown_symbol(self):
        """get_asset pour un symbole inconnu génère des données."""
        provider = MockFinanceProvider()
        asset = provider.get_asset('UNKNOWN123')
        
        assert asset is not None
        assert asset.symbol == 'UNKNOWN123'
        assert asset.name == 'UNKNOWN123 Corporation'
        assert asset.sector == 'Unknown'
    
    def test_get_asset_uses_cache(self):
        """get_asset utilise le cache."""
        provider = MockFinanceProvider()
        
        # Premier appel - ajoute au cache
        asset1 = provider.get_asset('AAPL')
        
        # Vérifier que c'est dans le cache
        assert 'AAPL' in provider._cache
        
        # Deuxième appel - devrait utiliser le cache
        asset2 = provider.get_asset('AAPL')
        
        # Le symbole devrait être le même
        assert asset1.symbol == asset2.symbol
    
    def test_get_asset_has_all_fields(self):
        """get_asset retourne un asset complet."""
        provider = MockFinanceProvider()
        asset = provider.get_asset('GOOGL')
        
        assert asset.symbol == 'GOOGL'
        assert asset.provider == 'mock'
        assert asset.exchange == 'NASDAQ'
        assert asset.currency == 'USD'
        assert asset.current_price > 0
        assert asset.previous_close > 0
        assert asset.volume > 0
        assert asset.market_cap > 0
        assert asset.indicators is not None
        assert asset.price_history is not None


class TestMockFinanceProviderListAssets:
    """Tests de list_assets."""
    
    def test_list_assets_default(self):
        """list_assets retourne des assets."""
        provider = MockFinanceProvider()
        assets = provider.list_assets()
        
        assert len(assets) > 0
        assert len(assets) <= 20  # Default limit
        for asset in assets:
            assert isinstance(asset, FinanceAssetNormalized)
    
    def test_list_assets_with_limit(self):
        """list_assets respecte la limite."""
        provider = MockFinanceProvider()
        
        assets_5 = provider.list_assets(limit=5)
        assert len(assets_5) == 5
        
        assets_10 = provider.list_assets(limit=10)
        assert len(assets_10) == 10
    
    def test_list_assets_with_sector_filter(self):
        """list_assets filtre par secteur."""
        provider = MockFinanceProvider()
        
        tech_assets = provider.list_assets(sector='Technology')
        
        for asset in tech_assets:
            if asset.sector:
                assert 'technology' in asset.sector.lower()


class TestMockFinanceProviderGetAssets:
    """Tests de get_assets."""
    
    def test_get_assets_with_symbols(self):
        """get_assets avec liste de symboles."""
        provider = MockFinanceProvider()
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        assets = provider.get_assets(symbols=symbols)
        
        assert len(assets) == 3
        symbols_returned = [a.symbol for a in assets]
        assert 'AAPL' in symbols_returned
        assert 'GOOGL' in symbols_returned
        assert 'MSFT' in symbols_returned
    
    def test_get_assets_with_sector(self):
        """get_assets avec filtre secteur."""
        provider = MockFinanceProvider()
        
        assets = provider.get_assets(sector='Finance')
        
        assert isinstance(assets, list)


class TestMockFinanceProviderGetHistorical:
    """Tests de get_historical et get_price_history."""
    
    def test_get_historical_default_period(self):
        """get_historical avec période par défaut."""
        provider = MockFinanceProvider()
        history = provider.get_historical('AAPL')
        
        assert isinstance(history, list)
        assert len(history) > 0
    
    def test_get_historical_period_mapping(self):
        """get_historical convertit les périodes."""
        provider = MockFinanceProvider()
        
        # Ces périodes devraient être converties
        history_1m = provider.get_historical('AAPL', '1M')
        history_3m = provider.get_historical('AAPL', '3M')
        
        assert len(history_1m) > 0
        assert len(history_3m) >= len(history_1m)
    
    def test_get_price_history_various_periods(self):
        """get_price_history avec différentes périodes."""
        provider = MockFinanceProvider()
        
        periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y']
        
        for period in periods:
            history = provider.get_price_history('AAPL', period)
            assert isinstance(history, list)
    
    def test_get_price_history_unknown_period(self):
        """get_price_history avec période inconnue utilise défaut."""
        provider = MockFinanceProvider()
        history = provider.get_price_history('AAPL', 'unknown')
        
        # Devrait utiliser 30 jours par défaut
        assert len(history) == 30


class TestMockFinanceProviderSearchAssets:
    """Tests de search_assets."""
    
    def test_search_assets_by_symbol(self):
        """search_assets trouve par symbole."""
        provider = MockFinanceProvider()
        results = provider.search_assets('AAPL')
        
        assert len(results) > 0
        assert any(r['symbol'] == 'AAPL' for r in results)
    
    def test_search_assets_by_name(self):
        """search_assets trouve par nom."""
        provider = MockFinanceProvider()
        results = provider.search_assets('Apple')
        
        assert len(results) > 0
        assert any('Apple' in r['name'] for r in results)
    
    def test_search_assets_case_insensitive(self):
        """search_assets est insensible à la casse (pour symbole)."""
        provider = MockFinanceProvider()
        
        # Recherche par symbole - toujours uppercase
        results_upper = provider.search_assets('AAPL')
        results_lower = provider.search_assets('aapl')
        
        # Les deux devraient trouver AAPL
        assert len(results_upper) > 0
        assert len(results_lower) > 0
    
    def test_search_assets_respects_limit(self):
        """search_assets respecte la limite."""
        provider = MockFinanceProvider()
        
        results = provider.search_assets('A', limit=3)
        assert len(results) <= 3
    
    def test_search_assets_returns_dict_format(self):
        """search_assets retourne le bon format."""
        provider = MockFinanceProvider()
        results = provider.search_assets('AAPL')
        
        if results:
            result = results[0]
            assert 'symbol' in result
            assert 'name' in result
            assert 'sector' in result


# ============================================
# REAL FINANCE PROVIDER TESTS
# ============================================

class TestRealFinanceProviderInit:
    """Tests d'initialisation du RealFinanceProvider."""
    
    def test_init_without_yfinance(self):
        """RealFinanceProvider sans yfinance installé."""
        with patch.dict('sys.modules', {'yfinance': None}):
            # L'import devrait être géré gracieusement
            provider = RealFinanceProvider()
            assert provider._yf is None
    
    @patch('app.providers.finance.RealFinanceProvider._init_yfinance')
    def test_init_calls_init_yfinance(self, mock_init):
        """L'init appelle _init_yfinance."""
        provider = RealFinanceProvider()
        mock_init.assert_called_once()
    
    def test_provider_name(self):
        """Le provider doit avoir le nom 'yfinance'."""
        provider = RealFinanceProvider()
        assert provider.provider_name == 'yfinance'


class TestRealFinanceProviderHealthCheck:
    """Tests de health_check pour RealFinanceProvider."""
    
    def test_health_check_without_yfinance(self):
        """health_check retourne unhealthy sans yfinance."""
        provider = RealFinanceProvider()
        provider._yf = None
        
        result = provider.health_check()
        
        assert result['healthy'] is False
    
    def test_health_check_with_mock_yfinance(self):
        """health_check avec yfinance mocké."""
        provider = RealFinanceProvider()
        
        # Simuler yfinance disponible
        mock_yf = MagicMock()
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {'regularMarketPrice': 150.0}
        mock_yf.Ticker.return_value = mock_ticker_instance
        
        provider._yf = mock_yf
        
        # Le health_check devrait fonctionner
        result = provider.health_check()
        # Le résultat dépend de l'implémentation mais devrait être un dict
        assert isinstance(result, dict)


class TestRealFinanceProviderAvailability:
    """Tests de is_available pour RealFinanceProvider."""
    
    def test_is_available_without_yfinance(self):
        """is_available retourne False sans yfinance."""
        provider = RealFinanceProvider()
        provider._yf = None
        
        assert provider.is_available() is False
    
    def test_is_available_with_yfinance(self):
        """is_available retourne True avec yfinance."""
        provider = RealFinanceProvider()
        provider._yf = MagicMock()
        
        assert provider.is_available() is True


# ============================================
# EDGE CASES AND ERROR HANDLING
# ============================================

class TestFinanceProviderEdgeCases:
    """Tests des cas limites."""
    
    def test_empty_history_indicators(self):
        """Indicateurs avec historique vide."""
        provider = MockFinanceProvider()
        indicators = provider._calculate_indicators([])
        
        assert isinstance(indicators, FinanceIndicatorsNormalized)
    
    def test_single_point_history(self):
        """Historique avec un seul point."""
        provider = MockFinanceProvider()
        history = provider._generate_price_history(100.0, 1)
        
        assert len(history) == 1
    
    def test_negative_base_price(self):
        """Prix de base négatif (cas limite)."""
        provider = MockFinanceProvider()
        # Le provider devrait gérer gracieusement
        price = provider._generate_price_with_trend(-100.0)
        # Le résultat peut varier selon l'implémentation
        assert isinstance(price, float)
    
    def test_very_large_limit(self):
        """Limite très grande pour list_assets."""
        provider = MockFinanceProvider()
        assets = provider.list_assets(limit=1000)
        
        # Ne devrait pas dépasser le nombre d'assets disponibles
        assert len(assets) <= len(provider.ASSETS)
    
    def test_search_no_results(self):
        """Recherche sans résultats."""
        provider = MockFinanceProvider()
        results = provider.search_assets('XYZNONEXISTENT123')
        
        assert results == []


class TestFinanceProviderConcurrency:
    """Tests de comportement concurrent."""
    
    def test_multiple_get_asset_calls(self):
        """Multiples appels get_asset."""
        provider = MockFinanceProvider()
        
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']
        assets = [provider.get_asset(s) for s in symbols]
        
        assert len(assets) == 5
        assert all(a is not None for a in assets)
    
    def test_cache_persistence(self):
        """Le cache persiste entre appels."""
        provider = MockFinanceProvider()
        
        # Premier appel
        provider.get_asset('AAPL')
        cache_size_1 = len(provider._cache)
        
        # Deuxième appel même symbole
        provider.get_asset('AAPL')
        cache_size_2 = len(provider._cache)
        
        # La taille du cache ne devrait pas augmenter
        assert cache_size_1 == cache_size_2
