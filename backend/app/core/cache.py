"""
Utilitaire de cache simple en mémoire pour réduire les appels API externes.
"""

import time
import logging
from typing import Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)


class SimpleCache:
    """Cache LRU simple en mémoire avec TTL."""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 60):
        """
        Initialise le cache.
        
        Args:
            max_size: Nombre maximum d'entrées
            default_ttl: Durée de vie par défaut en secondes
        """
        self.cache: dict = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache.
        
        Args:
            key: Clé de cache
            
        Returns:
            Valeur si présente et non expirée, None sinon
        """
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if time.time() > entry['expires_at']:
            del self.cache[key]
            return None
        
        entry['last_accessed'] = time.time()
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Stocke une valeur dans le cache.
        
        Args:
            key: Clé de cache
            value: Valeur à stocker
            ttl: Durée de vie en secondes (None = default_ttl)
        """
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'last_accessed': time.time()
        }
    
    def delete(self, key: str) -> None:
        """Supprime une entrée du cache."""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """Vide le cache."""
        self.cache.clear()
    
    def _evict_oldest(self) -> None:
        """Supprime l'entrée la moins récemment accédée."""
        if not self.cache:
            return
        
        oldest_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k]['last_accessed']
        )
        del self.cache[oldest_key]


# Cache global pour les API externes
external_api_cache = SimpleCache(max_size=200, default_ttl=60)


def cached(ttl: int = 60, key_prefix: str = ""):
    """
    Décorateur pour mettre en cache le résultat d'une fonction.
    
    Args:
        ttl: Durée de vie du cache en secondes
        key_prefix: Préfixe pour la clé de cache
        
    Usage:
        @cached(ttl=120, key_prefix="sports")
        def get_match_data(match_id: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Construire la clé de cache
            cache_key_parts = [key_prefix, func.__name__]
            cache_key_parts.extend(str(arg) for arg in args)
            cache_key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(filter(None, cache_key_parts))
            
            # Vérifier le cache
            cached_value = external_api_cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # Appeler la fonction et mettre en cache
            logger.debug(f"Cache miss for {cache_key}")
            result = func(*args, **kwargs)
            
            if result is not None:
                external_api_cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator
