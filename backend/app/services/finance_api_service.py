"""
Service API Finance.
Recupere les donnees boursieres depuis yfinance ou mock.

APIs supportees:
- yfinance (Yahoo Finance): https://pypi.org/project/yfinance/
- Alpha Vantage: https://www.alphavantage.co/
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

# Essayer d'importer yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    logger.warning("yfinance non disponible. Finance API en mode mock.")
    YFINANCE_AVAILABLE = False


class FinanceAPIService:
    """Service pour recuperer les donnees financieres."""
    
    def __init__(self):
        """Initialise le service API finance."""
        self.api_key = os.getenv('FINANCE_API_KEY', '')
        self.use_mock = (
            not YFINANCE_AVAILABLE or
            os.getenv('USE_MOCK_FINANCE_API', 'true').lower() == 'true'
        )
        
        if self.use_mock:
            logger.info("Finance API Service en mode MOCK")
        else:
            logger.info("Finance API Service initialise avec yfinance")

    def get_stock_data(self, ticker: str, period: str = '1mo') -> Optional[Dict[str, Any]]:
        """
        Recupere les donnees d'un actif financier.
        
        Args:
            ticker: Symbole boursier (ex: AAPL, GOOGL).
            period: Periode historique (1d, 5d, 1mo, 3mo, 6mo, 1y).
        
        Returns:
            Dictionnaire des donnees ou None si non trouve.
        """
        ticker = ticker.upper().strip()
        
        if self.use_mock:
            return self._get_mock_stock_data(ticker, period)
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                logger.warning(f"Aucune donnee pour ticker: {ticker}")
                return self._get_mock_stock_data(ticker, period)
            
            info = stock.info
            indicators = self._calculate_indicators(hist)
            
            return self._format_stock_data(ticker, info, hist, indicators)
            
        except Exception as e:
            logger.error(f"Erreur yfinance pour {ticker}: {e}")
            return self._get_mock_stock_data(ticker, period)

    def get_popular_stocks(
        self,
        sector: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Retourne une liste d'actifs populaires.
        
        Args:
            sector: Filtrer par secteur (optionnel).
            limit: Nombre max de resultats.
        
        Returns:
            Liste des actifs.
        """
        # Liste d'actifs populaires
        popular_tickers = [
            ('AAPL', 'Apple Inc.', 'Technology'),
            ('GOOGL', 'Alphabet Inc.', 'Technology'),
            ('MSFT', 'Microsoft Corporation', 'Technology'),
            ('AMZN', 'Amazon.com Inc.', 'Consumer Cyclical'),
            ('TSLA', 'Tesla Inc.', 'Consumer Cyclical'),
            ('META', 'Meta Platforms Inc.', 'Technology'),
            ('NVDA', 'NVIDIA Corporation', 'Technology'),
            ('JPM', 'JPMorgan Chase & Co.', 'Financial Services'),
            ('V', 'Visa Inc.', 'Financial Services'),
            ('JNJ', 'Johnson & Johnson', 'Healthcare'),
        ]
        
        if sector:
            popular_tickers = [t for t in popular_tickers if t[2] == sector]
        
        stocks = []
        for ticker, name, sect in popular_tickers[:limit]:
            stocks.append({
                'ticker': ticker,
                'name': name,
                'sector': sect
            })
        
        return stocks

    def _calculate_indicators(self, hist) -> Dict[str, Any]:
        """Calcule les indicateurs techniques."""
        close_prices = hist['Close']
        indicators = {}
        
        # Moyennes mobiles
        if len(close_prices) >= 5:
            indicators['MA_5'] = float(close_prices.tail(5).mean())
        if len(close_prices) >= 20:
            indicators['MA_20'] = float(close_prices.tail(20).mean())
        if len(close_prices) >= 50:
            indicators['MA_50'] = float(close_prices.tail(50).mean())
        
        # RSI simplifie
        if len(close_prices) >= 14:
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).tail(14).mean()
            loss = (-delta.where(delta < 0, 0)).tail(14).mean()
            
            if loss != 0:
                rs = gain / loss
                indicators['RSI'] = float(100 - (100 / (1 + rs)))
            else:
                indicators['RSI'] = 100.0
        
        # Volatilite
        if len(close_prices) >= 20:
            returns = close_prices.pct_change().dropna()
            indicators['volatility_daily'] = float(returns.std())
            indicators['volatility_annual'] = float(returns.std() * (252 ** 0.5))
        
        # Prix actuel et variation
        indicators['current_price'] = float(close_prices.iloc[-1])
        if len(close_prices) >= 2:
            change = ((close_prices.iloc[-1] - close_prices.iloc[-2]) / close_prices.iloc[-2]) * 100
            indicators['price_change_pct'] = float(change)
        
        return indicators

    def _format_stock_data(
        self,
        ticker: str,
        info: Dict,
        hist,
        indicators: Dict
    ) -> Dict[str, Any]:
        """Formate les donnees d'un actif."""
        # Convertir l'historique en liste
        prices = []
        for date, row in hist.iterrows():
            prices.append({
                'date': date.isoformat(),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })
        
        return {
            'symbol': ticker,
            'name': info.get('longName', ticker),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'currency': info.get('currency', 'USD'),
            'exchange': info.get('exchange', 'Unknown'),
            'market_cap': info.get('marketCap'),
            'current_price': indicators.get('current_price'),
            'price_change_pct': indicators.get('price_change_pct'),
            'prices': prices[-30:],  # Limiter a 30 derniers points
            'indicators': indicators
        }

    def _get_mock_stock_data(self, ticker: str, period: str) -> Optional[Dict[str, Any]]:
        """
        Genere des donnees mock pour un actif.
        
        PRODUCTION: Utiliser yfinance ou une vraie API.
        """
        # Donnees mock pour des tickers connus
        mock_stocks = {
            'AAPL': {
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'currency': 'USD',
                'exchange': 'NASDAQ',
                'market_cap': 2800000000000,
                'current_price': 175.50,
                'price_change_pct': 1.25,
            },
            'GOOGL': {
                'symbol': 'GOOGL',
                'name': 'Alphabet Inc.',
                'sector': 'Technology',
                'industry': 'Internet Content & Information',
                'currency': 'USD',
                'exchange': 'NASDAQ',
                'market_cap': 1700000000000,
                'current_price': 138.20,
                'price_change_pct': -0.45,
            },
            'MSFT': {
                'symbol': 'MSFT',
                'name': 'Microsoft Corporation',
                'sector': 'Technology',
                'industry': 'Software Infrastructure',
                'currency': 'USD',
                'exchange': 'NASDAQ',
                'market_cap': 2500000000000,
                'current_price': 378.90,
                'price_change_pct': 0.85,
            },
            'TSLA': {
                'symbol': 'TSLA',
                'name': 'Tesla Inc.',
                'sector': 'Consumer Cyclical',
                'industry': 'Auto Manufacturers',
                'currency': 'USD',
                'exchange': 'NASDAQ',
                'market_cap': 780000000000,
                'current_price': 245.30,
                'price_change_pct': -2.15,
            },
        }
        
        # Recuperer ou creer les donnees de base
        if ticker in mock_stocks:
            base_data = mock_stocks[ticker].copy()
        else:
            # Generer des donnees pour un ticker inconnu
            base_data = {
                'symbol': ticker,
                'name': f'{ticker} Corporation',
                'sector': 'Unknown',
                'industry': 'Unknown',
                'currency': 'USD',
                'exchange': 'NYSE',
                'market_cap': 50000000000,
                'current_price': 100.0 + random.uniform(-20, 20),
                'price_change_pct': random.uniform(-3, 3),
            }
        
        # Generer des prix historiques mock
        prices = self._generate_mock_prices(base_data['current_price'], period)
        
        # Calculer des indicateurs mock
        indicators = self._generate_mock_indicators(base_data['current_price'])
        
        base_data['prices'] = prices
        base_data['indicators'] = indicators
        
        return base_data

    def _generate_mock_prices(self, current_price: float, period: str) -> List[Dict]:
        """Genere des prix historiques mock."""
        # Determiner le nombre de jours selon la periode
        days_map = {
            '1d': 1,
            '5d': 5,
            '1mo': 22,
            '3mo': 66,
            '6mo': 132,
            '1y': 252
        }
        days = days_map.get(period, 22)
        
        prices = []
        price = current_price * (1 - random.uniform(0.05, 0.15))  # Commencer plus bas
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days - i)
            
            # Variation aleatoire
            change = random.uniform(-0.02, 0.025)
            price = price * (1 + change)
            
            prices.append({
                'date': date.isoformat(),
                'open': round(price * random.uniform(0.995, 1.005), 2),
                'high': round(price * random.uniform(1.005, 1.02), 2),
                'low': round(price * random.uniform(0.98, 0.995), 2),
                'close': round(price, 2),
                'volume': random.randint(1000000, 50000000)
            })
        
        return prices

    def _generate_mock_indicators(self, current_price: float) -> Dict[str, Any]:
        """Genere des indicateurs techniques mock."""
        return {
            'MA_5': round(current_price * random.uniform(0.98, 1.02), 2),
            'MA_20': round(current_price * random.uniform(0.95, 1.05), 2),
            'MA_50': round(current_price * random.uniform(0.90, 1.10), 2),
            'RSI': round(random.uniform(30, 70), 2),
            'volatility_daily': round(random.uniform(0.01, 0.04), 4),
            'volatility_annual': round(random.uniform(0.15, 0.50), 4),
            'current_price': current_price,
            'price_change_pct': round(random.uniform(-3, 3), 2)
        }


# Instance globale du service
finance_api_service = FinanceAPIService()
