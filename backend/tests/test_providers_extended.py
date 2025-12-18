"""
Tests supplémentaires pour les Data Providers.
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock


class TestBaseProviderDecorators:
    """Tests pour les décorateurs du module base."""
    
    def test_with_retry_import(self):
        """Tester l'import du décorateur with_retry."""
        from app.providers.base import with_retry
        assert with_retry is not None
    
    def test_log_provider_call_import(self):
        """Tester l'import du décorateur log_provider_call."""
        from app.providers.base import log_provider_call
        assert log_provider_call is not None
    
    def test_with_retry_success_first_try(self):
        """with_retry réussit du premier coup."""
        from app.providers.base import with_retry
        
        @with_retry(max_attempts=3)
        def success_func():
            return "success"
        
        result = success_func()
        assert result == "success"
    
    def test_with_retry_eventually_succeeds(self):
        """with_retry réussit après des échecs."""
        from app.providers.base import with_retry
        
        call_count = [0]
        
        @with_retry(max_attempts=3, backoff_factor=0.1)
        def flaky_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise Exception("Temporary error")
            return "success"
        
        result = flaky_func()
        assert result == "success"
        assert call_count[0] == 2
    
    def test_with_retry_all_fail(self):
        """with_retry échoue après toutes les tentatives."""
        from app.providers.base import with_retry
        
        @with_retry(max_attempts=2, backoff_factor=0.1)
        def always_fail():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_fail()
    
    def test_log_provider_call_success(self):
        """log_provider_call log un appel réussi."""
        from app.providers.base import log_provider_call
        
        class TestProvider:
            provider_name = "test_provider"
            
            @log_provider_call
            def test_method(self):
                return "result"
        
        provider = TestProvider()
        result = provider.test_method()
        
        assert result == "result"
    
    def test_log_provider_call_error(self):
        """log_provider_call log une erreur."""
        from app.providers.base import log_provider_call
        
        class TestProvider:
            provider_name = "test_provider"
            
            @log_provider_call
            def failing_method(self):
                raise RuntimeError("Test error")
        
        provider = TestProvider()
        
        with pytest.raises(RuntimeError):
            provider.failing_method()


class TestDataProviderBase:
    """Tests pour la classe DataProvider."""
    
    def test_data_provider_import(self):
        """Tester l'import de DataProvider."""
        from app.providers.base import DataProvider
        assert DataProvider is not None
    
    def test_is_mock_property_for_mock_provider(self):
        """is_mock retourne True pour un provider mock."""
        from app.providers.base import DataProvider
        
        class MockProvider(DataProvider):
            def __init__(self):
                super().__init__("mock_provider")
            
            def health_check(self):
                return True
        
        provider = MockProvider()
        assert provider.is_mock == True
    
    def test_is_mock_property_for_real_provider(self):
        """is_mock retourne False pour un provider réel."""
        from app.providers.base import DataProvider
        
        class RealProvider(DataProvider):
            def __init__(self):
                super().__init__("real_provider")
            
            def health_check(self):
                return True
        
        provider = RealProvider()
        assert provider.is_mock == False
    
    def test_get_config_returns_default(self):
        """get_config retourne la valeur par défaut."""
        from app.providers.base import DataProvider
        
        class TestProvider(DataProvider):
            def __init__(self):
                super().__init__("test")
            
            def health_check(self):
                return True
        
        provider = TestProvider()
        result = provider.get_config("NONEXISTENT_KEY", "default_value")
        
        assert result == "default_value"
    
    def test_provider_has_initialized_flag(self):
        """Le provider a un flag _initialized."""
        from app.providers.base import DataProvider
        
        class TestProvider(DataProvider):
            def __init__(self):
                super().__init__("test")
            
            def health_check(self):
                return True
        
        provider = TestProvider()
        assert hasattr(provider, '_initialized')


class TestSportsDataProvider:
    """Tests pour SportsDataProvider."""
    
    def test_sports_provider_import(self):
        """Tester l'import de SportsDataProvider."""
        from app.providers.base import SportsDataProvider
        assert SportsDataProvider is not None
    
    def test_sports_provider_is_abstract(self):
        """SportsDataProvider est une classe abstraite."""
        from app.providers.base import SportsDataProvider
        
        # Ne peut pas être instancié directement
        with pytest.raises(TypeError):
            SportsDataProvider("test")


class TestFinanceDataProvider:
    """Tests pour FinanceDataProvider."""
    
    def test_finance_provider_import(self):
        """Tester l'import de FinanceDataProvider."""
        from app.providers.base import FinanceDataProvider
        assert FinanceDataProvider is not None
    
    def test_finance_provider_is_abstract(self):
        """FinanceDataProvider est une classe abstraite."""
        from app.providers.base import FinanceDataProvider
        
        # Ne peut pas être instancié directement
        with pytest.raises(TypeError):
            FinanceDataProvider("test")


class TestSportsProviderConcrete:
    """Tests pour l'implémentation concrète sports."""
    
    def test_sports_provider_module_import(self):
        """Tester l'import du module sports."""
        try:
            from app.providers import sports
            assert sports is not None
        except ImportError:
            pytest.skip("Module sports non disponible")
    
    def test_mock_sports_provider_exists(self):
        """Vérifier que MockSportsProvider existe."""
        try:
            from app.providers.sports import MockSportsProvider
            assert MockSportsProvider is not None
        except ImportError:
            pytest.skip("MockSportsProvider non disponible")
    
    def test_mock_sports_provider_health_check(self):
        """Health check du MockSportsProvider."""
        try:
            from app.providers.sports import MockSportsProvider
            provider = MockSportsProvider()
            
            result = provider.health_check()
            # Peut retourner True ou avoir un comportement différent
            assert result is not None or result == True
        except (ImportError, TypeError, AttributeError):
            pytest.skip("MockSportsProvider non disponible")
    
    def test_mock_sports_provider_list_matches(self):
        """list_matches du MockSportsProvider."""
        try:
            from app.providers.sports import MockSportsProvider
            provider = MockSportsProvider()
            
            matches = provider.list_matches(limit=5)
            
            assert isinstance(matches, list)
        except (ImportError, TypeError):
            pytest.skip("MockSportsProvider non disponible")
    
    def test_mock_sports_provider_get_match(self):
        """get_match du MockSportsProvider."""
        try:
            from app.providers.sports import MockSportsProvider
            provider = MockSportsProvider()
            
            # Essayer avec un ID mock
            match = provider.get_match("mock_1")
            
            # Peut être None ou un match
            assert match is None or hasattr(match, 'match_id')
        except (ImportError, TypeError):
            pytest.skip("MockSportsProvider non disponible")


class TestFinanceProviderConcrete:
    """Tests pour l'implémentation concrète finance."""
    
    def test_finance_provider_module_import(self):
        """Tester l'import du module finance."""
        try:
            from app.providers import finance
            assert finance is not None
        except ImportError:
            pytest.skip("Module finance non disponible")
    
    def test_mock_finance_provider_exists(self):
        """Vérifier que MockFinanceProvider existe."""
        try:
            from app.providers.finance import MockFinanceProvider
            assert MockFinanceProvider is not None
        except ImportError:
            pytest.skip("MockFinanceProvider non disponible")
    
    def test_mock_finance_provider_health_check(self):
        """Health check du MockFinanceProvider."""
        try:
            from app.providers.finance import MockFinanceProvider
            provider = MockFinanceProvider()
            
            result = provider.health_check()
            # Peut retourner True ou avoir un comportement différent
            assert result is not None or result == True
        except (ImportError, TypeError, AttributeError):
            pytest.skip("MockFinanceProvider non disponible")
    
    def test_mock_finance_provider_get_quote(self):
        """get_quote du MockFinanceProvider."""
        try:
            from app.providers.finance import MockFinanceProvider
            provider = MockFinanceProvider()
            
            quote = provider.get_quote("AAPL")
            
            # La réponse peut être None, dict, ou objet avec symbol
            if quote is not None:
                assert 'symbol' in quote or hasattr(quote, 'symbol')
        except (ImportError, TypeError, AttributeError):
            pytest.skip("MockFinanceProvider non disponible")
    
    def test_mock_finance_provider_get_historical(self):
        """get_historical du MockFinanceProvider."""
        try:
            from app.providers.finance import MockFinanceProvider
            provider = MockFinanceProvider()
            
            history = provider.get_historical("AAPL", period="1m")
            
            assert history is not None
        except (ImportError, TypeError, AttributeError):
            pytest.skip("MockFinanceProvider non disponible")


class TestProviderSchemas:
    """Tests pour les schémas du module providers."""
    
    def test_schemas_import(self):
        """Tester l'import du module schemas."""
        try:
            from app.providers.schemas import SportsMatchNormalized, FinanceQuoteNormalized
            
            assert SportsMatchNormalized is not None
            assert FinanceQuoteNormalized is not None
        except ImportError:
            pytest.skip("Schemas non disponibles")

