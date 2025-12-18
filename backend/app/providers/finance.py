"""
Finance Data Providers.

Providers disponibles:
- MockFinanceProvider: Données simulées pour dev/tests
- RealFinanceProvider: yfinance (Yahoo Finance)

Sélection via env: USE_MOCK_FINANCE_API=true/false
"""

import os
import logging
import random
import math
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from app.providers.base import FinanceDataProvider, with_retry, log_provider_call
from app.providers.schemas import (
    FinanceAssetNormalized,
    FinanceIndicatorsNormalized,
    FinancePricePoint,
)
from app.core.cache import cached

logger = logging.getLogger(__name__)


# ============================================
# MOCK FINANCE PROVIDER
# ============================================

class MockFinanceProvider(FinanceDataProvider):
    """
    Provider mock pour les données financières.
    
    Génère des données réalistes basées sur des tickers connus.
    """
    
    # Données de base pour les actifs populaires
    ASSETS = {
        'AAPL': {'name': 'Apple Inc.', 'sector': 'Technology', 'base_price': 175.0},
        'GOOGL': {'name': 'Alphabet Inc.', 'sector': 'Technology', 'base_price': 140.0},
        'MSFT': {'name': 'Microsoft Corporation', 'sector': 'Technology', 'base_price': 380.0},
        'AMZN': {'name': 'Amazon.com Inc.', 'sector': 'Consumer Cyclical', 'base_price': 180.0},
        'TSLA': {'name': 'Tesla Inc.', 'sector': 'Consumer Cyclical', 'base_price': 250.0},
        'META': {'name': 'Meta Platforms Inc.', 'sector': 'Technology', 'base_price': 500.0},
        'NVDA': {'name': 'NVIDIA Corporation', 'sector': 'Technology', 'base_price': 480.0},
        'JPM': {'name': 'JPMorgan Chase & Co.', 'sector': 'Financial Services', 'base_price': 195.0},
        'V': {'name': 'Visa Inc.', 'sector': 'Financial Services', 'base_price': 280.0},
        'JNJ': {'name': 'Johnson & Johnson', 'sector': 'Healthcare', 'base_price': 155.0},
        'WMT': {'name': 'Walmart Inc.', 'sector': 'Consumer Defensive', 'base_price': 165.0},
        'PG': {'name': 'Procter & Gamble Co.', 'sector': 'Consumer Defensive', 'base_price': 160.0},
        'UNH': {'name': 'UnitedHealth Group Inc.', 'sector': 'Healthcare', 'base_price': 520.0},
        'HD': {'name': 'Home Depot Inc.', 'sector': 'Consumer Cyclical', 'base_price': 380.0},
        'BAC': {'name': 'Bank of America Corp.', 'sector': 'Financial Services', 'base_price': 35.0},
        'XOM': {'name': 'Exxon Mobil Corporation', 'sector': 'Energy', 'base_price': 105.0},
        'CVX': {'name': 'Chevron Corporation', 'sector': 'Energy', 'base_price': 150.0},
        'KO': {'name': 'Coca-Cola Company', 'sector': 'Consumer Defensive', 'base_price': 60.0},
        'PEP': {'name': 'PepsiCo Inc.', 'sector': 'Consumer Defensive', 'base_price': 170.0},
        'DIS': {'name': 'Walt Disney Company', 'sector': 'Communication Services', 'base_price': 95.0},
    }
    
    def __init__(self):
        super().__init__('mock-finance')
        self._cache: Dict[str, FinanceAssetNormalized] = {}
        logger.info("MockFinanceProvider initialized")
    
    def health_check(self) -> Dict[str, Any]:
        """Health check du mock provider."""
        return {
            'healthy': True,
            'provider': 'MockFinanceProvider',
            'assets_available': len(self.ASSETS)
        }
    
    def is_available(self) -> bool:
        """Mock provider toujours disponible."""
        return True
    
    def _generate_price_with_trend(self, base_price: float, volatility: float = 0.02) -> float:
        """Génère un prix avec variation aléatoire."""
        change = random.gauss(0, volatility)
        return round(base_price * (1 + change), 2)
    
    def _generate_price_history(
        self,
        base_price: float,
        days: int = 30
    ) -> List[FinancePricePoint]:
        """Génère un historique de prix réaliste."""
        history = []
        current_price = base_price * random.uniform(0.9, 1.0)  # Démarrer légèrement différent
        
        now = datetime.now()
        
        for i in range(days, 0, -1):
            date = now - timedelta(days=i)
            
            # Variation journalière
            daily_return = random.gauss(0.0005, 0.02)  # Légèrement haussier
            current_price *= (1 + daily_return)
            
            # OHLC réaliste
            day_volatility = abs(random.gauss(0, 0.01))
            open_price = current_price * (1 + random.uniform(-day_volatility, day_volatility))
            high = max(open_price, current_price) * (1 + random.uniform(0, day_volatility))
            low = min(open_price, current_price) * (1 - random.uniform(0, day_volatility))
            close = current_price
            
            volume = int(random.uniform(5_000_000, 50_000_000))
            
            history.append(FinancePricePoint(
                date=date,
                open=round(open_price, 2),
                high=round(high, 2),
                low=round(low, 2),
                close=round(close, 2),
                volume=volume,
            ))
        
        return history
    
    def _calculate_indicators(self, history: List[FinancePricePoint]) -> FinanceIndicatorsNormalized:
        """Calcule les indicateurs techniques à partir de l'historique."""
        if len(history) < 20:
            return FinanceIndicatorsNormalized()
        
        closes = [p.close for p in history]
        
        # SMA
        sma_20 = sum(closes[-20:]) / 20
        sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None
        
        # RSI (simplifié)
        gains = []
        losses = []
        for i in range(1, min(15, len(closes))):
            change = closes[-i] - closes[-i-1]
            if change > 0:
                gains.append(change)
            else:
                losses.append(abs(change))
        
        avg_gain = sum(gains) / 14 if gains else 0
        avg_loss = sum(losses) / 14 if losses else 0.001
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # MACD (simplifié)
        ema_12 = sum(closes[-12:]) / 12 if len(closes) >= 12 else closes[-1]
        ema_26 = sum(closes[-26:]) / 26 if len(closes) >= 26 else closes[-1]
        macd = ema_12 - ema_26
        
        # Bollinger Bands
        std_dev = (sum((c - sma_20) ** 2 for c in closes[-20:]) / 20) ** 0.5
        
        return FinanceIndicatorsNormalized(
            sma_20=round(sma_20, 2),
            sma_50=round(sma_50, 2) if sma_50 else None,
            rsi_14=round(rsi, 2),
            macd=round(macd, 4),
            ema_12=round(ema_12, 2),
            ema_26=round(ema_26, 2),
            bollinger_upper=round(sma_20 + 2 * std_dev, 2),
            bollinger_middle=round(sma_20, 2),
            bollinger_lower=round(sma_20 - 2 * std_dev, 2),
        )
    
    @log_provider_call
    def get_asset(self, symbol: str) -> Optional[FinanceAssetNormalized]:
        """Récupère un actif par symbole."""
        symbol = symbol.upper().strip()
        
        # Vérifier le cache
        if symbol in self._cache:
            cached = self._cache[symbol]
            # Mettre à jour le prix actuel
            cached.current_price = self._generate_price_with_trend(cached.current_price, 0.005)
            cached.last_updated = datetime.now()
            return cached
        
        # Données connues ou générées
        if symbol in self.ASSETS:
            asset_data = self.ASSETS[symbol]
        else:
            # Générer des données pour un symbole inconnu
            asset_data = {
                'name': f'{symbol} Corporation',
                'sector': 'Unknown',
                'base_price': random.uniform(20, 500)
            }
        
        base_price = asset_data['base_price']
        current_price = self._generate_price_with_trend(base_price)
        previous_close = self._generate_price_with_trend(base_price, 0.01)
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100
        
        history = self._generate_price_history(base_price)
        indicators = self._calculate_indicators(history)
        
        asset = FinanceAssetNormalized(
            symbol=symbol,
            name=asset_data['name'],
            provider='mock',
            exchange='NASDAQ',
            currency='USD',
            sector=asset_data['sector'],
            current_price=current_price,
            previous_close=previous_close,
            open_price=self._generate_price_with_trend(previous_close, 0.005),
            day_high=current_price * random.uniform(1.0, 1.02),
            day_low=current_price * random.uniform(0.98, 1.0),
            change=round(change, 2),
            change_percent=round(change_percent, 2),
            volume=random.randint(10_000_000, 100_000_000),
            avg_volume=random.randint(20_000_000, 80_000_000),
            market_cap=int(current_price * random.randint(1_000_000_000, 50_000_000_000)),
            indicators=indicators,
            price_history=history,
        )
        
        self._cache[symbol] = asset
        return asset
    
    @log_provider_call
    def list_assets(
        self,
        sector: Optional[str] = None,
        exchange: Optional[str] = None,
        min_market_cap: Optional[int] = None,
        limit: int = 20
    ) -> List[FinanceAssetNormalized]:
        """Liste les actifs avec filtres."""
        assets = []
        
        for symbol in list(self.ASSETS.keys())[:limit]:
            asset = self.get_asset(symbol)
            if asset:
                # Filtrer par secteur
                if sector and asset.sector and sector.lower() not in asset.sector.lower():
                    continue
                assets.append(asset)
        
        return assets[:limit]
    
    def get_assets(
        self,
        symbols: Optional[List[str]] = None,
        sector: Optional[str] = None,
        limit: int = 20
    ) -> List[FinanceAssetNormalized]:
        """Alias pour list_assets avec filtre par symbols."""
        if symbols:
            assets = []
            for symbol in symbols:
                asset = self.get_asset(symbol)
                if asset:
                    assets.append(asset)
            return assets[:limit]
        return self.list_assets(sector=sector, limit=limit)
    
    def get_historical(
        self,
        symbol: str,
        period: str = '1M'
    ) -> List[FinancePricePoint]:
        """Alias pour get_price_history."""
        # Normaliser le format de période
        period_map = {'1M': '1mo', '3M': '3mo', '6M': '6mo', '1Y': '1y'}
        normalized = period_map.get(period.upper(), period.lower())
        return self.get_price_history(symbol, normalized)
    
    @log_provider_call
    def get_price_history(
        self,
        symbol: str,
        period: str = '1mo'
    ) -> List[FinancePricePoint]:
        """Récupère l'historique des prix."""
        # Mapper période vers nombre de jours
        period_days = {
            '1d': 1,
            '5d': 5,
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
        }
        days = period_days.get(period, 30)
        
        asset = self.get_asset(symbol)
        if not asset:
            return []
        
        # Regénérer avec le bon nombre de jours si nécessaire
        if len(asset.price_history) < days:
            base_price = self.ASSETS.get(symbol.upper(), {}).get('base_price', 100)
            return self._generate_price_history(base_price, days)
        
        return asset.price_history[-days:]
    
    def search_assets(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """Recherche d'actifs."""
        query = query.upper()
        results = []
        
        for symbol, data in self.ASSETS.items():
            if query in symbol or query in data['name'].upper():
                results.append({
                    'symbol': symbol,
                    'name': data['name'],
                    'sector': data['sector'],
                })
        
        return results[:limit]


# ============================================
# REAL FINANCE PROVIDER (yfinance)
# ============================================

class RealFinanceProvider(FinanceDataProvider):
    """
    Provider réel utilisant yfinance (Yahoo Finance).
    
    Nécessite:
    - yfinance package installé
    """
    
    def __init__(self):
        super().__init__('yfinance')
        self._yf = None
        self._init_yfinance()
    
    def _init_yfinance(self):
        """Initialise yfinance."""
        try:
            import yfinance as yf
            self._yf = yf
            logger.info("yfinance initialized successfully")
        except ImportError:
            logger.error("yfinance not installed. Run: pip install yfinance")
            self._yf = None
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie que yfinance est disponible."""
        if self._yf is None:
            return {
                'healthy': False,
                'provider': 'RealFinanceProvider',
                'error': 'yfinance not installed'
            }
        try:
            # Test rapide avec un ticker connu
            ticker = self._yf.Ticker("AAPL")
            info = ticker.fast_info
            return {
                'healthy': hasattr(info, 'last_price'),
                'provider': 'RealFinanceProvider',
            }
        except Exception as e:
            logger.error(f"yfinance health check failed: {e}")
            return {
                'healthy': False,
                'provider': 'RealFinanceProvider',
                'error': str(e)
            }
    
    def is_available(self) -> bool:
        """Vérifie si yfinance est disponible."""
        return self._yf is not None
    
    @cached(ttl=60, key_prefix="finance_real")
    @with_retry(max_attempts=2, backoff_factor=1.0, timeout=10.0)
    @log_provider_call
    def get_asset(self, symbol: str) -> Optional[FinanceAssetNormalized]:
        """Récupère un actif depuis Yahoo Finance."""
        if self._yf is None:
            return None
        
        symbol = symbol.upper().strip()
        
        try:
            ticker = self._yf.Ticker(symbol)
            info = ticker.info
            fast_info = ticker.fast_info
            
            if not info or 'symbol' not in info:
                return None
            
            # Récupérer l'historique pour les indicateurs
            hist = ticker.history(period='3mo')
            history = self._map_history(hist)
            indicators = self._calculate_indicators_from_history(history)
            
            current_price = fast_info.get('lastPrice', info.get('currentPrice', 0))
            previous_close = fast_info.get('previousClose', info.get('previousClose', current_price))
            change = current_price - previous_close if previous_close else 0
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            return FinanceAssetNormalized(
                symbol=symbol,
                name=info.get('longName', info.get('shortName', symbol)),
                provider='yfinance',
                exchange=info.get('exchange'),
                currency=info.get('currency', 'USD'),
                sector=info.get('sector'),
                industry=info.get('industry'),
                country=info.get('country'),
                current_price=round(current_price, 2),
                previous_close=round(previous_close, 2) if previous_close else None,
                open_price=round(fast_info.get('open', 0), 2) if fast_info.get('open') else None,
                day_high=round(fast_info.get('dayHigh', 0), 2) if fast_info.get('dayHigh') else None,
                day_low=round(fast_info.get('dayLow', 0), 2) if fast_info.get('dayLow') else None,
                change=round(change, 2),
                change_percent=round(change_percent, 2),
                volume=int(fast_info.get('lastVolume', 0)),
                avg_volume=int(info.get('averageVolume', 0)),
                market_cap=int(info.get('marketCap', 0)) if info.get('marketCap') else None,
                indicators=indicators,
                price_history=history[-30:],  # Derniers 30 jours
            )
            
        except Exception as e:
            logger.error(f"Error fetching {symbol} from yfinance: {e}")
            return None
    
    def _map_history(self, hist) -> List[FinancePricePoint]:
        """Mappe l'historique yfinance vers notre format."""
        history = []
        
        for date, row in hist.iterrows():
            try:
                history.append(FinancePricePoint(
                    date=date.to_pydatetime(),
                    open=round(row['Open'], 2),
                    high=round(row['High'], 2),
                    low=round(row['Low'], 2),
                    close=round(row['Close'], 2),
                    volume=int(row['Volume']),
                ))
            except Exception:
                continue
        
        return history
    
    def _calculate_indicators_from_history(
        self,
        history: List[FinancePricePoint]
    ) -> FinanceIndicatorsNormalized:
        """Calcule les indicateurs techniques."""
        if len(history) < 20:
            return FinanceIndicatorsNormalized()
        
        closes = [p.close for p in history]
        
        # SMA
        sma_20 = sum(closes[-20:]) / 20
        sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None
        
        # RSI
        gains = []
        losses = []
        for i in range(1, min(15, len(closes))):
            change = closes[-i] - closes[-i-1]
            if change > 0:
                gains.append(change)
            else:
                losses.append(abs(change))
        
        avg_gain = sum(gains) / 14 if gains else 0
        avg_loss = sum(losses) / 14 if losses else 0.001
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return FinanceIndicatorsNormalized(
            sma_20=round(sma_20, 2),
            sma_50=round(sma_50, 2) if sma_50 else None,
            rsi_14=round(rsi, 2),
        )
    
    @cached(ttl=300, key_prefix="finance_list")
    @log_provider_call
    def list_assets(
        self,
        sector: Optional[str] = None,
        exchange: Optional[str] = None,
        min_market_cap: Optional[int] = None,
        limit: int = 20
    ) -> List[FinanceAssetNormalized]:
        """Liste les actifs populaires."""
        # Liste statique d'actifs populaires
        popular = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'JNJ']
        
        assets = []
        for symbol in popular[:limit]:
            asset = self.get_asset(symbol)
            if asset:
                if sector and asset.sector and sector.lower() not in asset.sector.lower():
                    continue
                assets.append(asset)
        
        return assets
    
    @cached(ttl=120, key_prefix="finance_history")
    @log_provider_call
    def get_price_history(
        self,
        symbol: str,
        period: str = '1mo'
    ) -> List[FinancePricePoint]:
        """Récupère l'historique des prix."""
        if self._yf is None:
            return []
        
        try:
            ticker = self._yf.Ticker(symbol.upper())
            hist = ticker.history(period=period)
            return self._map_history(hist)
        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {e}")
            return []


# ============================================
# FACTORY FUNCTION
# ============================================

_finance_provider_instance: Optional[FinanceDataProvider] = None


def get_finance_provider() -> FinanceDataProvider:
    """
    Factory pour obtenir le provider finance configuré.
    
    Sélection basée sur USE_MOCK_FINANCE_API:
    - true (défaut): MockFinanceProvider
    - false: RealFinanceProvider (nécessite yfinance)
    
    Returns:
        Instance singleton du provider
    """
    global _finance_provider_instance
    
    if _finance_provider_instance is None:
        use_mock = os.getenv('USE_MOCK_FINANCE_API', 'true').lower() == 'true'
        
        if use_mock:
            _finance_provider_instance = MockFinanceProvider()
        else:
            # Vérifier que yfinance est disponible
            try:
                import yfinance
                _finance_provider_instance = RealFinanceProvider()
            except ImportError:
                logger.warning(
                    "yfinance not installed, falling back to MockFinanceProvider"
                )
                _finance_provider_instance = MockFinanceProvider()
        
        logger.info(f"Finance provider initialized: {_finance_provider_instance.provider_name}")
    
    return _finance_provider_instance


def reset_finance_provider():
    """Reset le singleton (utile pour les tests)."""
    global _finance_provider_instance
    _finance_provider_instance = None
