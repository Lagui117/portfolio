"""
Finance API Service for PredictWise.

This service handles fetching financial/stock market data from external APIs.
Currently using yfinance (Yahoo Finance) as the primary provider.

Alternative APIs you can use:
- Alpha Vantage: https://www.alphavantage.co/
- IEX Cloud: https://iexcloud.io/
- Twelve Data: https://twelvedata.com/
- Polygon.io: https://polygon.io/
"""
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

# Essayer d'importer yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    logger.warning("yfinance not installed. Finance API will use mock data only.")
    YFINANCE_AVAILABLE = False


class FinanceAPIService:
    """Service for fetching stock/financial market data."""
    
    def __init__(self):
        """Initialize the finance API service."""
        self.api_key = os.getenv('FINANCE_API_KEY', '')
        self.use_mock = not YFINANCE_AVAILABLE or os.getenv('USE_MOCK_FINANCE_API', 'false').lower() == 'true'
        
        if self.use_mock:
            logger.warning("Finance API running in MOCK mode.")
        else:
            logger.info("Finance API service initialized with yfinance")
    
    def get_stock_data(self, ticker: str, period: str = '1mo') -> Dict[str, Any]:
        """
        Get stock market data and technical indicators.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
            period: Time period for historical data (1d, 5d, 1mo, 3mo, 6mo, 1y)
        
        Returns:
            Dictionary containing stock data and indicators
        
        Raises:
            ValueError: If ticker is invalid or data unavailable
        """
        ticker = ticker.upper().strip()
        
        if self.use_mock or not YFINANCE_AVAILABLE:
            return self._get_mock_stock_data(ticker, period)
        
        try:
            # Récupérer les données avec yfinance
            stock = yf.Ticker(ticker)
            
            # Récupérer l'historique
            hist = stock.history(period=period)
            
            if hist.empty:
                logger.warning(f"No data found for ticker: {ticker}")
                return self._get_mock_stock_data(ticker, period)
            
            # Récupérer les infos de base
            info = stock.info
            
            # Calculer les indicateurs techniques
            indicators = self._calculate_indicators(hist)
            
            # Formater les données
            return self._format_stock_data(ticker, info, hist, indicators)
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {ticker}: {e}")
            logger.info("Falling back to mock data")
            return self._get_mock_stock_data(ticker, period)
    
    def _calculate_indicators(self, hist: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators from price history."""
        close_prices = hist['Close']
        
        indicators = {}
        
        # Moving Averages
        if len(close_prices) >= 5:
            indicators['MA_5'] = close_prices.tail(5).mean()
        if len(close_prices) >= 20:
            indicators['MA_20'] = close_prices.tail(20).mean()
        if len(close_prices) >= 50:
            indicators['MA_50'] = close_prices.tail(50).mean()
        
        # RSI (Relative Strength Index) - simplifié
        if len(close_prices) >= 14:
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).tail(14).mean()
            loss = (-delta.where(delta < 0, 0)).tail(14).mean()
            
            if loss != 0:
                rs = gain / loss
                indicators['RSI'] = 100 - (100 / (1 + rs))
            else:
                indicators['RSI'] = 100
        
        # Volatility
        if len(close_prices) >= 20:
            returns = close_prices.pct_change().dropna()
            indicators['volatility_daily'] = returns.std()
            indicators['volatility_annual'] = returns.std() * (252 ** 0.5)  # Annualisée
        
        # Current price and change
        indicators['current_price'] = close_prices.iloc[-1]
        if len(close_prices) >= 2:
            indicators['price_change_pct'] = ((close_prices.iloc[-1] - close_prices.iloc[-2]) / close_prices.iloc[-2]) * 100
        
        # Volume
        if 'Volume' in hist.columns:
            indicators['avg_volume'] = hist['Volume'].tail(20).mean()
            indicators['current_volume'] = hist['Volume'].iloc[-1]
        
        return indicators
    
    def _format_stock_data(self, ticker: str, info: Dict, hist: pd.DataFrame, indicators: Dict) -> Dict[str, Any]:
        """Format stock data into standardized structure."""
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
            'indicators': {
                'MA_5': indicators.get('MA_5'),
                'MA_20': indicators.get('MA_20'),
                'MA_50': indicators.get('MA_50'),
                'RSI': indicators.get('RSI'),
                'volatility_daily': indicators.get('volatility_daily'),
                'volatility_annual': indicators.get('volatility_annual'),
                'avg_volume': indicators.get('avg_volume'),
                'current_volume': indicators.get('current_volume')
            },
            'historical_data': {
                'period': hist.index[0].strftime('%Y-%m-%d') + ' to ' + hist.index[-1].strftime('%Y-%m-%d'),
                'data_points': len(hist),
                'high': hist['High'].max(),
                'low': hist['Low'].min(),
                'avg_close': hist['Close'].mean()
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_mock_stock_data(self, ticker: str, period: str = '1mo') -> Dict[str, Any]:
        """
        Generate mock stock data for testing/demo purposes.
        
        PRODUCTION: Replace this with actual API calls to:
        - Alpha Vantage: https://www.alphavantage.co/
        - IEX Cloud: https://iexcloud.io/
        - Twelve Data: https://twelvedata.com/
        """
        import random
        
        # Données simulées pour quelques tickers populaires
        mock_stocks = {
            'AAPL': {
                'name': 'Apple Inc.',
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'base_price': 185.00
            },
            'GOOGL': {
                'name': 'Alphabet Inc.',
                'sector': 'Technology',
                'industry': 'Internet Content & Information',
                'base_price': 140.00
            },
            'MSFT': {
                'name': 'Microsoft Corporation',
                'sector': 'Technology',
                'industry': 'Software',
                'base_price': 375.00
            },
            'TSLA': {
                'name': 'Tesla Inc.',
                'sector': 'Automotive',
                'industry': 'Auto Manufacturers',
                'base_price': 245.00
            },
            'AMZN': {
                'name': 'Amazon.com Inc.',
                'sector': 'Consumer Cyclical',
                'industry': 'Internet Retail',
                'base_price': 155.00
            }
        }
        
        # Utiliser les données mock ou générer aléatoirement
        if ticker in mock_stocks:
            stock_info = mock_stocks[ticker]
        else:
            stock_info = {
                'name': f'{ticker} Corporation',
                'sector': 'Unknown',
                'industry': 'Unknown',
                'base_price': random.uniform(50, 500)
            }
        
        current_price = stock_info['base_price'] * random.uniform(0.95, 1.05)
        price_change = random.uniform(-5, 5)
        
        return {
            'symbol': ticker,
            'name': stock_info['name'],
            'sector': stock_info['sector'],
            'industry': stock_info['industry'],
            'currency': 'USD',
            'exchange': 'NASDAQ',
            'market_cap': int(current_price * random.uniform(1e9, 1e12)),
            'current_price': round(current_price, 2),
            'price_change_pct': round(price_change, 2),
            'indicators': {
                'MA_5': round(current_price * random.uniform(0.98, 1.02), 2),
                'MA_20': round(current_price * random.uniform(0.95, 1.05), 2),
                'MA_50': round(current_price * random.uniform(0.90, 1.10), 2),
                'RSI': round(random.uniform(30, 70), 2),
                'volatility_daily': round(random.uniform(0.01, 0.05), 4),
                'volatility_annual': round(random.uniform(0.15, 0.60), 4),
                'avg_volume': int(random.uniform(1e6, 1e8)),
                'current_volume': int(random.uniform(1e6, 1e8))
            },
            'historical_data': {
                'period': period,
                'data_points': 30 if period == '1mo' else 90,
                'high': round(current_price * 1.15, 2),
                'low': round(current_price * 0.85, 2),
                'avg_close': round(current_price, 2)
            },
            'timestamp': datetime.now().isoformat(),
            'mock_data': True  # Indicateur que ce sont des données simulées
        }
    
    def get_market_overview(self) -> Dict[str, Any]:
        """Get general market overview with major indices."""
        indices = ['SPY', 'QQQ', 'DIA']  # S&P 500, NASDAQ, Dow Jones ETFs
        
        overview = {
            'timestamp': datetime.now().isoformat(),
            'indices': {}
        }
        
        for index in indices:
            try:
                data = self.get_stock_data(index, period='5d')
                overview['indices'][index] = {
                    'price': data.get('current_price'),
                    'change_pct': data.get('price_change_pct')
                }
            except Exception as e:
                logger.error(f"Error fetching index {index}: {e}")
        
        return overview


# Instance globale du service
finance_api_service = FinanceAPIService()
