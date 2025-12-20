"""
Tests pour le système Live (cache, scheduler, SSE).
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import json

# Import des modules à tester
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.live import (
    LiveCache, 
    BackgroundScheduler, 
    SSEManager,
    ResourceType,
    RESOURCE_TTL,
    live_cache,
    CachedData,
)


class TestResourceType:
    """Tests pour l'enum ResourceType."""
    
    def test_resource_types_exist(self):
        """Vérifie que tous les types de ressources sont définis."""
        assert ResourceType.FINANCE_TICKER is not None
        assert ResourceType.FINANCE_LIST is not None
        assert ResourceType.SPORTS_MATCH is not None
        assert ResourceType.SPORTS_LIST is not None
        assert ResourceType.AI_ANALYSIS is not None
    
    def test_ttl_values(self):
        """Vérifie que les TTL sont raisonnables."""
        for resource_type in ResourceType:
            ttl = RESOURCE_TTL.get(resource_type, 60)
            assert ttl >= 5, f"TTL trop court pour {resource_type}"
            assert ttl <= 600, f"TTL trop long pour {resource_type}"


class TestLiveCache:
    """Tests pour LiveCache."""
    
    def setup_method(self):
        """Prépare un cache propre avant chaque test."""
        self.cache = LiveCache()
    
    def test_set_and_get(self):
        """Test basique set/get."""
        self.cache.set(ResourceType.FINANCE_TICKER, "AAPL", {"price": 150.0})
        
        result = self.cache.get(ResourceType.FINANCE_TICKER, "AAPL")
        
        assert result is not None
        assert result["price"] == 150.0
    
    def test_get_nonexistent(self):
        """Test get sur clé inexistante."""
        result = self.cache.get(ResourceType.FINANCE_TICKER, "NONEXISTENT")
        assert result is None
    
    def test_ttl_expiration(self):
        """Test que les données expirent après TTL."""
        # Utiliser un TTL très court pour le test
        self.cache.set(ResourceType.FINANCE_TICKER, "TEST", {"value": 1}, ttl=0.1)
        
        # Données présentes immédiatement
        assert self.cache.get(ResourceType.FINANCE_TICKER, "TEST") is not None
        
        # Attendre l'expiration
        time.sleep(0.2)
        
        # Données expirées
        assert self.cache.get(ResourceType.FINANCE_TICKER, "TEST") is None
    
    def test_data_versioning(self):
        """Test que le versioning des données fonctionne."""
        data1 = {"price": 100.0}
        data2 = {"price": 100.0}  # Mêmes données
        data3 = {"price": 101.0}  # Données différentes
        
        self.cache.set(ResourceType.FINANCE_TICKER, "AAPL", data1)
        version1 = self.cache.get_version(ResourceType.FINANCE_TICKER, "AAPL")
        
        self.cache.set(ResourceType.FINANCE_TICKER, "AAPL", data2)
        version2 = self.cache.get_version(ResourceType.FINANCE_TICKER, "AAPL")
        
        self.cache.set(ResourceType.FINANCE_TICKER, "AAPL", data3)
        version3 = self.cache.get_version(ResourceType.FINANCE_TICKER, "AAPL")
        
        # Mêmes données = même version
        assert version1 == version2
        # Données différentes = version différente
        assert version2 != version3
    
    def test_cache_stats(self):
        """Test des statistiques de cache."""
        # Quelques hits et misses
        self.cache.set(ResourceType.FINANCE_TICKER, "AAPL", {"price": 150})
        self.cache.get(ResourceType.FINANCE_TICKER, "AAPL")  # Hit
        self.cache.get(ResourceType.FINANCE_TICKER, "AAPL")  # Hit
        self.cache.get(ResourceType.FINANCE_TICKER, "MISSING")  # Miss
        
        stats = self.cache.get_stats()
        
        assert stats["hits"] >= 2
        assert stats["misses"] >= 1
        assert stats["entries"] >= 1
    
    def test_invalidate_single(self):
        """Test d'invalidation d'une entrée."""
        self.cache.set(ResourceType.FINANCE_TICKER, "AAPL", {"price": 150})
        self.cache.set(ResourceType.FINANCE_TICKER, "GOOG", {"price": 2800})
        
        self.cache.invalidate(ResourceType.FINANCE_TICKER, "AAPL")
        
        assert self.cache.get(ResourceType.FINANCE_TICKER, "AAPL") is None
        assert self.cache.get(ResourceType.FINANCE_TICKER, "GOOG") is not None
    
    def test_invalidate_by_type(self):
        """Test d'invalidation par type."""
        self.cache.set(ResourceType.FINANCE_TICKER, "AAPL", {"price": 150})
        self.cache.set(ResourceType.FINANCE_TICKER, "GOOG", {"price": 2800})
        self.cache.set(ResourceType.SPORTS_MATCH, "match1", {"score": "1-0"})
        
        self.cache.invalidate_type(ResourceType.FINANCE_TICKER)
        
        assert self.cache.get(ResourceType.FINANCE_TICKER, "AAPL") is None
        assert self.cache.get(ResourceType.FINANCE_TICKER, "GOOG") is None
        assert self.cache.get(ResourceType.SPORTS_MATCH, "match1") is not None
    
    def test_clear_all(self):
        """Test du clear complet."""
        self.cache.set(ResourceType.FINANCE_TICKER, "AAPL", {"price": 150})
        self.cache.set(ResourceType.SPORTS_MATCH, "match1", {"score": "1-0"})
        
        self.cache.clear()
        
        stats = self.cache.get_stats()
        assert stats["entries"] == 0
    
    def test_thread_safety(self):
        """Test de la sécurité thread."""
        errors = []
        
        def writer():
            try:
                for i in range(100):
                    self.cache.set(ResourceType.FINANCE_TICKER, f"SYM{i}", {"value": i})
            except Exception as e:
                errors.append(e)
        
        def reader():
            try:
                for i in range(100):
                    self.cache.get(ResourceType.FINANCE_TICKER, f"SYM{i}")
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=writer),
            threading.Thread(target=reader),
            threading.Thread(target=writer),
            threading.Thread(target=reader),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Thread errors: {errors}"


class TestBackgroundScheduler:
    """Tests pour BackgroundScheduler."""
    
    def test_scheduler_creation(self):
        """Test de création du scheduler."""
        scheduler = BackgroundScheduler()
        assert not scheduler.is_running()
    
    def test_add_job(self):
        """Test d'ajout de job."""
        scheduler = BackgroundScheduler()
        
        job_executed = threading.Event()
        
        def test_job():
            job_executed.set()
        
        scheduler.add_job("test_job", test_job, interval=0.1)
        scheduler.start()
        
        try:
            # Attendre que le job s'exécute
            assert job_executed.wait(timeout=1.0), "Job never executed"
        finally:
            scheduler.stop()
    
    def test_remove_job(self):
        """Test de suppression de job."""
        scheduler = BackgroundScheduler()
        execution_count = [0]
        
        def counter_job():
            execution_count[0] += 1
        
        scheduler.add_job("counter", counter_job, interval=0.05)
        scheduler.start()
        
        time.sleep(0.15)
        scheduler.remove_job("counter")
        count_at_removal = execution_count[0]
        
        time.sleep(0.1)
        
        scheduler.stop()
        
        # Le compteur ne devrait plus augmenter après suppression
        assert execution_count[0] == count_at_removal or execution_count[0] == count_at_removal + 1
    
    def test_scheduler_stop(self):
        """Test d'arrêt du scheduler."""
        scheduler = BackgroundScheduler()
        execution_count = [0]
        
        def counter_job():
            execution_count[0] += 1
        
        scheduler.add_job("counter", counter_job, interval=0.05)
        scheduler.start()
        
        assert scheduler.is_running()
        
        time.sleep(0.1)
        scheduler.stop()
        
        assert not scheduler.is_running()


class TestSSEManager:
    """Tests pour SSEManager."""
    
    def setup_method(self):
        """Prépare un manager propre."""
        self.sse = SSEManager()
    
    def test_client_registration(self):
        """Test d'enregistrement de client."""
        client_id = self.sse.register_client("user123")
        
        assert client_id is not None
        assert self.sse.client_count() == 1
    
    def test_client_unregistration(self):
        """Test de désenregistrement."""
        client_id = self.sse.register_client("user123")
        self.sse.unregister_client(client_id)
        
        assert self.sse.client_count() == 0
    
    def test_channel_subscription(self):
        """Test d'abonnement à un canal."""
        client_id = self.sse.register_client("user123")
        
        self.sse.subscribe(client_id, "finance_AAPL")
        
        subscriptions = self.sse.get_subscriptions(client_id)
        assert "finance_AAPL" in subscriptions
    
    def test_broadcast_to_channel(self):
        """Test de broadcast sur un canal."""
        received_messages = []
        
        # Simuler un générateur client
        def mock_generator():
            while True:
                msg = yield
                if msg:
                    received_messages.append(msg)
        
        client_id = self.sse.register_client("user123")
        self.sse.subscribe(client_id, "test_channel")
        
        # Le broadcast devrait fonctionner sans erreur
        self.sse.broadcast("test_channel", {"data": "test"})


class TestCachedData:
    """Tests pour la dataclass CachedData."""
    
    def test_is_expired_false(self):
        """Test données non expirées."""
        cached = CachedData(
            data={"test": 1},
            expires_at=time.time() + 100,  # Expire dans 100s
            data_version="v1",
            created_at=time.time(),
        )
        
        assert not cached.is_expired()
    
    def test_is_expired_true(self):
        """Test données expirées."""
        cached = CachedData(
            data={"test": 1},
            expires_at=time.time() - 1,  # Expiré il y a 1s
            data_version="v1",
            created_at=time.time() - 10,
        )
        
        assert cached.is_expired()


class TestLiveEndpoints:
    """Tests d'intégration pour les endpoints live."""
    
    @pytest.fixture
    def client(self):
        """Crée un client de test Flask."""
        from app.main import create_app
        
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def auth_headers(self, client):
        """Crée les headers avec token d'auth."""
        # Créer un utilisateur de test et obtenir un token
        # (Simplifié pour le test)
        return {"Authorization": "Bearer test_token"}
    
    def test_live_config_endpoint(self, client):
        """Test de l'endpoint /live/config."""
        response = client.get('/api/v1/live/config')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert "enabled" in data
        assert "polling_intervals" in data
        assert "ttl" in data


class TestIntegration:
    """Tests d'intégration du système live complet."""
    
    def test_cache_with_scheduler(self):
        """Test du cache avec le scheduler."""
        cache = LiveCache()
        scheduler = BackgroundScheduler()
        
        update_count = [0]
        
        def update_cache():
            update_count[0] += 1
            cache.set(
                ResourceType.FINANCE_TICKER, 
                "AAPL", 
                {"price": 150 + update_count[0]}
            )
        
        scheduler.add_job("update_aapl", update_cache, interval=0.1)
        scheduler.start()
        
        time.sleep(0.35)
        scheduler.stop()
        
        # Le cache devrait avoir été mis à jour plusieurs fois
        assert update_count[0] >= 2
        
        data = cache.get(ResourceType.FINANCE_TICKER, "AAPL")
        assert data is not None
        assert data["price"] > 150


# Configuration pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
