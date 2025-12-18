"""
Base classes pour les Data Providers.

Architecture:
- DataProvider: Classe de base abstraite
- SportsDataProvider: Interface pour les données sportives
- FinanceDataProvider: Interface pour les données financières

Chaque provider concret (Mock, Real) hérite de ces classes.
"""

import os
import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, TypeVar, Generic
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


# ============================================
# DECORATEURS UTILITAIRES
# ============================================

def with_retry(max_attempts: int = 3, backoff_factor: float = 1.5, timeout: float = 5.0):
    """
    Décorateur pour retry avec backoff exponentiel.
    
    Args:
        max_attempts: Nombre max de tentatives
        backoff_factor: Multiplicateur de délai entre tentatives
        timeout: Timeout par requête en secondes
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    latency_ms = (time.time() - start_time) * 1000
                    
                    logger.debug(f"{func.__name__} succeeded in {latency_ms:.2f}ms (attempt {attempt})")
                    return result
                    
                except Exception as e:
                    last_exception = e
                    wait_time = backoff_factor ** (attempt - 1)
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    
                    if attempt < max_attempts:
                        time.sleep(wait_time)
            
            logger.error(f"{func.__name__} failed after {max_attempts} attempts")
            raise last_exception
        
        return wrapper
    return decorator


def log_provider_call(func):
    """Décorateur pour logger les appels provider avec métriques."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        provider_name = getattr(self, 'provider_name', self.__class__.__name__)
        start_time = time.time()
        cache_hit = False
        
        try:
            result = func(self, *args, **kwargs)
            latency_ms = (time.time() - start_time) * 1000
            
            logger.info(
                f"[{provider_name}] {func.__name__} | "
                f"latency={latency_ms:.2f}ms | "
                f"status=success | "
                f"cache_hit={cache_hit}"
            )
            return result
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(
                f"[{provider_name}] {func.__name__} | "
                f"latency={latency_ms:.2f}ms | "
                f"status=error | "
                f"error={str(e)}"
            )
            raise
    
    return wrapper


# ============================================
# BASE PROVIDER
# ============================================

class DataProvider(ABC):
    """
    Classe de base abstraite pour tous les providers.
    
    Responsabilités:
    - Définir l'interface commune
    - Gérer la configuration
    - Fournir des utilitaires (logging, metrics)
    """
    
    def __init__(self, provider_name: str):
        """
        Initialise le provider.
        
        Args:
            provider_name: Nom unique du provider (pour logs/metrics)
        """
        self.provider_name = provider_name
        self._initialized = False
        self._config: Dict[str, Any] = {}
    
    @abstractmethod
    def health_check(self) -> bool:
        """
        Vérifie que le provider est opérationnel.
        
        Returns:
            True si le provider peut répondre aux requêtes.
        """
        pass
    
    @property
    def is_mock(self) -> bool:
        """Indique si c'est un provider mock."""
        return 'mock' in self.provider_name.lower()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration."""
        return self._config.get(key, os.getenv(key, default))


# ============================================
# SPORTS PROVIDER INTERFACE
# ============================================

class SportsDataProvider(DataProvider):
    """
    Interface pour les providers de données sportives.
    
    Méthodes à implémenter:
    - get_match(match_id) -> SportsMatchNormalized
    - list_matches(filters) -> List[SportsMatchNormalized]
    - get_live_matches() -> List[SportsMatchNormalized]
    """
    
    @abstractmethod
    def get_match(self, match_id: str) -> Optional['SportsMatchNormalized']:
        """
        Récupère un match par son ID.
        
        Args:
            match_id: Identifiant unique du match
            
        Returns:
            Match normalisé ou None si non trouvé
        """
        pass
    
    @abstractmethod
    def list_matches(
        self,
        competition: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List['SportsMatchNormalized']:
        """
        Liste les matchs avec filtres.
        
        Args:
            competition: Filtrer par compétition
            date_from: Date de début (ISO format)
            date_to: Date de fin (ISO format)
            status: Filtrer par status (scheduled, live, finished)
            limit: Nombre max de résultats
            
        Returns:
            Liste de matchs normalisés
        """
        pass
    
    @abstractmethod
    def get_live_matches(self) -> List['SportsMatchNormalized']:
        """
        Récupère les matchs en cours.
        
        Returns:
            Liste des matchs live
        """
        pass
    
    def get_team_stats(self, team_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les stats d'une équipe.
        
        Par défaut retourne None. Les providers réels peuvent override.
        """
        return None


# ============================================
# FINANCE PROVIDER INTERFACE
# ============================================

class FinanceDataProvider(DataProvider):
    """
    Interface pour les providers de données financières.
    
    Méthodes à implémenter:
    - get_asset(symbol) -> FinanceAssetNormalized
    - list_assets(filters) -> List[FinanceAssetNormalized]
    - get_price_history(symbol, period) -> List[FinancePricePoint]
    """
    
    @abstractmethod
    def get_asset(self, symbol: str) -> Optional['FinanceAssetNormalized']:
        """
        Récupère un actif par son symbole.
        
        Args:
            symbol: Symbole boursier (ex: AAPL, GOOGL)
            
        Returns:
            Actif normalisé ou None si non trouvé
        """
        pass
    
    @abstractmethod
    def list_assets(
        self,
        sector: Optional[str] = None,
        exchange: Optional[str] = None,
        min_market_cap: Optional[int] = None,
        limit: int = 20
    ) -> List['FinanceAssetNormalized']:
        """
        Liste les actifs avec filtres.
        
        Args:
            sector: Filtrer par secteur
            exchange: Filtrer par bourse
            min_market_cap: Capitalisation minimum
            limit: Nombre max de résultats
            
        Returns:
            Liste d'actifs normalisés
        """
        pass
    
    @abstractmethod
    def get_price_history(
        self,
        symbol: str,
        period: str = '1mo'
    ) -> List['FinancePricePoint']:
        """
        Récupère l'historique des prix.
        
        Args:
            symbol: Symbole boursier
            period: Période (1d, 5d, 1mo, 3mo, 6mo, 1y)
            
        Returns:
            Liste de points de prix
        """
        pass
    
    def search_assets(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Recherche d'actifs par nom/symbole.
        
        Par défaut retourne une liste vide.
        """
        return []


# Import des schemas (pour les type hints)
from app.providers.schemas import SportsMatchNormalized, FinanceAssetNormalized, FinancePricePoint
