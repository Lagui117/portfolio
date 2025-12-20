"""
Live Data Management - Cache avancé, versioning et scheduler.

Ce module gère:
- Cache TTL intelligent par ressource
- Versioning des données (ETag/data_version)
- Scheduler pour background updates
- SSE (Server-Sent Events) support
"""

import time
import hashlib
import json
import logging
import threading
from datetime import datetime
from typing import Any, Optional, Dict, Callable, List
from functools import wraps
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types de ressources avec TTL configurables."""
    FINANCE_TICKER = "finance:ticker"
    FINANCE_LIST = "finance:list"
    SPORTS_MATCH = "sports:match"
    SPORTS_LIST = "sports:list"
    AI_ANALYSIS = "ai:analysis"
    DASHBOARD = "dashboard"


# Configuration TTL par type de ressource (en secondes)
RESOURCE_TTL = {
    ResourceType.FINANCE_TICKER: 15,      # Prix actualisés fréquemment
    ResourceType.FINANCE_LIST: 60,        # Liste stocks moins fréquent
    ResourceType.SPORTS_MATCH: 30,        # Matchs en cours
    ResourceType.SPORTS_LIST: 120,        # Liste matchs
    ResourceType.AI_ANALYSIS: 300,        # Analyses IA (5 min)
    ResourceType.DASHBOARD: 60,           # Dashboard stats
}

# Intervalle de polling recommandé (en secondes)
POLLING_INTERVALS = {
    "fast": {"finance": 10, "sports": 30, "dashboard": 30},
    "normal": {"finance": 30, "sports": 60, "dashboard": 60},
    "eco": {"finance": 60, "sports": 120, "dashboard": 120},
}


@dataclass
class CachedData:
    """Données cachées avec métadonnées."""
    value: Any
    data_version: str
    created_at: float
    expires_at: float
    updated_at: float
    hit_count: int = 0
    resource_type: Optional[ResourceType] = None
    
    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at
    
    @property
    def age_seconds(self) -> float:
        return time.time() - self.created_at
    
    def to_metadata(self) -> Dict[str, Any]:
        """Retourne les métadonnées pour la réponse API."""
        return {
            "data_version": self.data_version,
            "updated_at": datetime.fromtimestamp(self.updated_at).isoformat(),
            "cached": True,
            "cache_age_seconds": round(self.age_seconds, 1),
            "ttl_remaining": max(0, round(self.expires_at - time.time(), 1)),
        }


class LiveCache:
    """
    Cache avancé avec versioning et TTL par ressource.
    Thread-safe avec support pour updates background.
    """
    
    def __init__(self, max_size: int = 500):
        self._cache: Dict[str, CachedData] = {}
        self._lock = threading.RLock()
        self._max_size = max_size
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
        }
        
    def _generate_version(self, data: Any) -> str:
        """Génère un hash de version pour les données."""
        try:
            serialized = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(serialized.encode()).hexdigest()[:12]
        except Exception:
            return hashlib.md5(str(data).encode()).hexdigest()[:12]
    
    def _make_key(self, resource_type: ResourceType, identifier: str) -> str:
        """Crée une clé de cache standardisée."""
        return f"{resource_type.value}:{identifier}"
    
    def get(
        self, 
        resource_type: ResourceType, 
        identifier: str,
        check_version: Optional[str] = None
    ) -> Optional[CachedData]:
        """
        Récupère des données du cache.
        
        Args:
            resource_type: Type de ressource
            identifier: Identifiant unique (ticker, match_id, etc.)
            check_version: Si fourni, retourne None si version identique (304)
            
        Returns:
            CachedData si trouvé et valide, None sinon
        """
        key = self._make_key(resource_type, identifier)
        
        with self._lock:
            if key not in self._cache:
                self._stats["misses"] += 1
                return None
            
            cached = self._cache[key]
            
            if cached.is_expired:
                del self._cache[key]
                self._stats["misses"] += 1
                return None
            
            # Vérifier si données inchangées (304 Not Modified)
            if check_version and cached.data_version == check_version:
                cached.hit_count += 1
                self._stats["hits"] += 1
                return cached  # Le caller peut retourner 304
            
            cached.hit_count += 1
            self._stats["hits"] += 1
            return cached
    
    def set(
        self,
        resource_type: ResourceType,
        identifier: str,
        value: Any,
        ttl: Optional[int] = None,
        force_version: Optional[str] = None
    ) -> CachedData:
        """
        Stocke des données dans le cache.
        
        Args:
            resource_type: Type de ressource
            identifier: Identifiant unique
            value: Données à cacher
            ttl: TTL custom (sinon utilise RESOURCE_TTL)
            force_version: Version à utiliser (sinon générée)
            
        Returns:
            CachedData créé
        """
        key = self._make_key(resource_type, identifier)
        ttl = ttl or RESOURCE_TTL.get(resource_type, 60)
        now = time.time()
        
        data_version = force_version or self._generate_version(value)
        
        cached = CachedData(
            value=value,
            data_version=data_version,
            created_at=now,
            updated_at=now,
            expires_at=now + ttl,
            resource_type=resource_type,
        )
        
        with self._lock:
            # Eviction si cache plein
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_oldest()
            
            self._cache[key] = cached
        
        logger.debug(f"Cache SET: {key} (version={data_version}, ttl={ttl}s)")
        return cached
    
    def invalidate(self, resource_type: ResourceType, identifier: str) -> bool:
        """Invalide une entrée de cache."""
        key = self._make_key(resource_type, identifier)
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
        return False
    
    def invalidate_pattern(self, resource_type: ResourceType) -> int:
        """Invalide toutes les entrées d'un type."""
        prefix = resource_type.value
        count = 0
        with self._lock:
            keys_to_delete = [k for k in self._cache if k.startswith(prefix)]
            for key in keys_to_delete:
                del self._cache[key]
                count += 1
        return count
    
    def _evict_oldest(self) -> None:
        """Supprime l'entrée la plus ancienne."""
        if not self._cache:
            return
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at
        )
        del self._cache[oldest_key]
        self._stats["evictions"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache."""
        with self._lock:
            total = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0
            return {
                **self._stats,
                "size": len(self._cache),
                "max_size": self._max_size,
                "hit_rate_percent": round(hit_rate, 2),
            }
    
    def clear(self) -> int:
        """Vide le cache."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count


# Instance globale du cache live
live_cache = LiveCache(max_size=500)


def live_cached(
    resource_type: ResourceType,
    key_param: str = None,
    ttl: Optional[int] = None
):
    """
    Décorateur pour cache live avec versioning.
    
    Args:
        resource_type: Type de ressource
        key_param: Nom du paramètre à utiliser comme clé (ex: 'ticker', 'match_id')
        ttl: TTL custom
        
    Usage:
        @live_cached(ResourceType.FINANCE_TICKER, key_param='ticker')
        def get_stock(ticker: str):
            return fetch_from_api(ticker)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extraire l'identifiant
            if key_param:
                identifier = kwargs.get(key_param) or (args[0] if args else "default")
            else:
                identifier = str(args) + str(sorted(kwargs.items()))
            
            identifier = str(identifier).lower()
            
            # Vérifier le cache
            client_version = kwargs.pop('_client_version', None)
            cached = live_cache.get(resource_type, identifier, check_version=client_version)
            
            if cached:
                # Ajouter métadonnées à la réponse
                result = cached.value
                if isinstance(result, dict):
                    result['_cache_meta'] = cached.to_metadata()
                return result
            
            # Exécuter la fonction
            result = func(*args, **kwargs)
            
            # Mettre en cache
            cached = live_cache.set(resource_type, identifier, result, ttl=ttl)
            
            if isinstance(result, dict):
                result['_cache_meta'] = cached.to_metadata()
                result['_cache_meta']['cached'] = False
            
            return result
        
        return wrapper
    return decorator


# ============================================
# BACKGROUND SCHEDULER
# ============================================

class BackgroundScheduler:
    """
    Scheduler simple pour updates en background.
    Utilise des threads pour les tâches périodiques.
    """
    
    def __init__(self):
        self._jobs: Dict[str, Dict] = {}
        self._running = False
        self._threads: List[threading.Thread] = []
    
    def add_job(
        self,
        job_id: str,
        func: Callable,
        interval_seconds: int,
        args: tuple = (),
        kwargs: dict = None
    ):
        """Ajoute une tâche périodique."""
        self._jobs[job_id] = {
            "func": func,
            "interval": interval_seconds,
            "args": args,
            "kwargs": kwargs or {},
            "last_run": 0,
            "run_count": 0,
            "errors": 0,
        }
        logger.info(f"Scheduler: Job '{job_id}' ajouté (interval={interval_seconds}s)")
    
    def remove_job(self, job_id: str) -> bool:
        """Supprime une tâche."""
        if job_id in self._jobs:
            del self._jobs[job_id]
            return True
        return False
    
    def _run_job(self, job_id: str):
        """Exécute une tâche en boucle."""
        job = self._jobs.get(job_id)
        if not job:
            return
        
        while self._running and job_id in self._jobs:
            try:
                job["func"](*job["args"], **job["kwargs"])
                job["run_count"] += 1
                job["last_run"] = time.time()
            except Exception as e:
                job["errors"] += 1
                logger.error(f"Scheduler: Erreur job '{job_id}': {e}")
            
            time.sleep(job["interval"])
    
    def start(self):
        """Démarre le scheduler."""
        if self._running:
            return
        
        self._running = True
        
        for job_id in self._jobs:
            thread = threading.Thread(
                target=self._run_job,
                args=(job_id,),
                daemon=True,
                name=f"scheduler-{job_id}"
            )
            thread.start()
            self._threads.append(thread)
        
        logger.info(f"Scheduler: Démarré avec {len(self._jobs)} jobs")
    
    def stop(self):
        """Arrête le scheduler."""
        self._running = False
        logger.info("Scheduler: Arrêté")
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le status du scheduler."""
        return {
            "running": self._running,
            "jobs": {
                job_id: {
                    "interval": job["interval"],
                    "run_count": job["run_count"],
                    "errors": job["errors"],
                    "last_run": datetime.fromtimestamp(job["last_run"]).isoformat() 
                        if job["last_run"] > 0 else None,
                }
                for job_id, job in self._jobs.items()
            }
        }


# Instance globale du scheduler
background_scheduler = BackgroundScheduler()


# ============================================
# SSE (Server-Sent Events) Support
# ============================================

class SSEManager:
    """
    Gestionnaire de connexions SSE.
    Permet le push de données vers les clients connectés.
    """
    
    def __init__(self):
        self._clients: Dict[str, Dict] = {}  # client_id -> {queue, subscriptions}
        self._lock = threading.Lock()
    
    def register_client(self, client_id: str, subscriptions: List[str] = None):
        """Enregistre un nouveau client SSE."""
        from queue import Queue
        with self._lock:
            self._clients[client_id] = {
                "queue": Queue(),
                "subscriptions": set(subscriptions or []),
                "connected_at": time.time(),
            }
        logger.debug(f"SSE: Client {client_id} connecté")
    
    def unregister_client(self, client_id: str):
        """Déconnecte un client SSE."""
        with self._lock:
            if client_id in self._clients:
                del self._clients[client_id]
        logger.debug(f"SSE: Client {client_id} déconnecté")
    
    def broadcast(self, event_type: str, data: Any, channel: str = "global"):
        """
        Envoie un événement à tous les clients abonnés.
        
        Args:
            event_type: Type d'événement (ex: 'finance:update', 'sports:update')
            data: Données à envoyer
            channel: Canal de diffusion
        """
        message = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "channel": channel,
        }
        
        with self._lock:
            for client_id, client in self._clients.items():
                if channel in client["subscriptions"] or "global" in client["subscriptions"]:
                    try:
                        client["queue"].put_nowait(message)
                    except Exception:
                        pass
    
    def get_client_queue(self, client_id: str):
        """Retourne la queue d'un client."""
        with self._lock:
            client = self._clients.get(client_id)
            return client["queue"] if client else None
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques SSE."""
        with self._lock:
            return {
                "connected_clients": len(self._clients),
                "clients": list(self._clients.keys()),
            }


# Instance globale du gestionnaire SSE
sse_manager = SSEManager()


# ============================================
# HELPER: Response with versioning
# ============================================

def make_live_response(
    data: Any,
    resource_type: ResourceType = None,
    identifier: str = None,
    cache_meta: Dict = None
) -> Dict[str, Any]:
    """
    Crée une réponse API standardisée avec métadonnées live.
    
    Args:
        data: Données de la réponse
        resource_type: Type de ressource (pour génération version)
        identifier: Identifiant de la ressource
        cache_meta: Métadonnées de cache existantes
        
    Returns:
        Dict avec données + métadonnées live
    """
    response = data if isinstance(data, dict) else {"data": data}
    
    # Générer version si pas de cache_meta
    if not cache_meta:
        version = hashlib.md5(
            json.dumps(data, sort_keys=True, default=str).encode()
        ).hexdigest()[:12]
        
        response["_live"] = {
            "data_version": version,
            "updated_at": datetime.utcnow().isoformat(),
            "resource_type": resource_type.value if resource_type else None,
            "identifier": identifier,
        }
    else:
        response["_live"] = {
            "data_version": cache_meta.get("data_version"),
            "updated_at": cache_meta.get("updated_at"),
            "cached": cache_meta.get("cached", False),
            "ttl_remaining": cache_meta.get("ttl_remaining"),
        }
    
    return response
