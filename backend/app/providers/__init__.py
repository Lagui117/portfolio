"""
Data Providers - Abstraction pour les sources de données externes.

Ce module fournit une architecture unifiée pour accéder aux données
sportives et financières, avec support pour:
- Providers Mock (développement/tests)
- Providers Réels (APIs externes)
- Normalisation des données
- Cache et retry automatique
"""

from app.providers.base import DataProvider, SportsDataProvider, FinanceDataProvider
from app.providers.sports import get_sports_provider, MockSportsProvider, RealSportsProvider
from app.providers.finance import get_finance_provider, MockFinanceProvider, RealFinanceProvider
from app.providers.schemas import (
    SportsMatchNormalized,
    SportsTeamNormalized,
    SportsStatsNormalized,
    FinanceAssetNormalized,
    FinanceIndicatorsNormalized,
    FinancePricePoint,
)

__all__ = [
    # Base classes
    'DataProvider',
    'SportsDataProvider', 
    'FinanceDataProvider',
    # Factory functions
    'get_sports_provider',
    'get_finance_provider',
    # Provider implementations
    'MockSportsProvider',
    'RealSportsProvider',
    'MockFinanceProvider',
    'RealFinanceProvider',
    # Schemas
    'SportsMatchNormalized',
    'SportsTeamNormalized',
    'SportsStatsNormalized',
    'FinanceAssetNormalized',
    'FinanceIndicatorsNormalized',
    'FinancePricePoint',
]
