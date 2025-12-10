"""Finance data service with ML predictions and technical indicators."""
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import joblib
import pandas as pd
import numpy as np
from app.models.stock_asset import StockAsset, StockPrice
from app.core.database import db


class FinanceService:
    """Service for fetching financial data and making ML predictions."""
    
    def __init__(self):
        self.api_key = os.getenv('FINANCE_API_KEY', '')
        self.model = None
        self.scaler = None
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load the trained ML model and scaler for finance predictions."""
        model_path = os.path.join(
            os.path.dirname(__file__),
            '../../ml/models/finance_model.pkl'
        )
        scaler_path = os.path.join(
            os.path.dirname(__file__),
            '../../ml/models/finance_scaler.pkl'
        )
        
        try:
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.model_loaded = True
                print(f"Finance ML model and scaler loaded")
            else:
                print(f"Finance model not found. Using fallback predictions.")
        except Exception as e:
            print(f"Failed to load finance model: {e}")
            self.model_loaded = False
    
    def get_stock_data(
        self, 
        symbol: str, 
        period: str = '1mo', 
        interval: str = '1d'
    ) -> List[Dict]:
        """
        Fetch stock market data.
        
        Args:
            symbol: Stock symbol (e.g., AAPL, GOOGL)
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y)
            interval: Data interval (1m, 5m, 1h, 1d)
            
        Returns:
            List of price data dictionaries
        """
        symbol = symbol.upper()
        
        # Try to get from database first
        days_map = {'1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365}
        days = days_map.get(period, 30)
        
        start_date = datetime.now().date() - timedelta(days=days)
        
        prices = StockPrice.query.filter(
            StockPrice.symbol == symbol,
            StockPrice.date >= start_date
        ).order_by(StockPrice.date).all()
        
        if prices:
            return [p.to_dict() for p in prices]
        
        # If not in DB, generate mock data
        return self._get_mock_stock_data(symbol, days)
    
    def calculate_indicators(
        self, 
        symbol: str, 
        period: str = '1mo',
        indicators: List[str] = None
    ) -> Dict:
        """
        Calculate technical indicators.
        
        Args:
            symbol: Stock symbol
            period: Time period
            indicators: List of indicators to calculate (MA, RSI, VOLATILITY, MACD)
            
        Returns:
            Dictionary of calculated indicators
        """
        if indicators is None:
            indicators = ['MA', 'RSI', 'VOLATILITY']
        
        # Get stock data
        data = self.get_stock_data(symbol, period)
        if not data:
            return {}
        
        df = pd.DataFrame(data)
        if df.empty or 'close' not in df.columns:
            return {}
        
        results = {}
        
        # Moving Averages
        if 'MA' in indicators:
            if len(df) >= 5:
                results['MA_5'] = float(df['close'].tail(5).mean())
            if len(df) >= 20:
                results['MA_20'] = float(df['close'].tail(20).mean())
            if len(df) >= 50:
                results['MA_50'] = float(df['close'].tail(50).mean())
        
        # RSI (Relative Strength Index)
        if 'RSI' in indicators:
            rsi = self._calculate_rsi(df['close'])
            if rsi is not None:
                results['RSI'] = float(rsi)
        
        # Volatility
        if 'VOLATILITY' in indicators:
            returns = df['close'].pct_change()
            daily_vol = returns.std()
            annual_vol = daily_vol * np.sqrt(252)  # Annualized
            results['volatility_daily'] = float(daily_vol)
            results['volatility_annual'] = float(annual_vol)
        
        # MACD
        if 'MACD' in indicators and len(df) >= 26:
            macd_line, signal_line = self._calculate_macd(df['close'])
            if macd_line is not None:
                results['MACD'] = float(macd_line)
                results['MACD_signal'] = float(signal_line)
        
        # Add current price
        results['current_price'] = float(df['close'].iloc[-1])
        results['price_change'] = float(df['close'].iloc[-1] - df['close'].iloc[0])
        results['price_change_pct'] = float(
            ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
        )
        
        return results
    
    def predict_trend(
        self, 
        symbol: str, 
        period: str = '1mo'
    ) -> Dict:
        """
        Predict price trend (UP/DOWN) using ML model.
        
        Args:
            symbol: Stock symbol
            period: Historical period to analyze
            
        Returns:
            Prediction dictionary with trend and confidence
        """
        # Get historical data
        data = self.get_stock_data(symbol, period)
        if not data or len(data) < 20:
            return {
                'error': 'Données insuffisantes pour la prédiction',
                'min_required': 20,
                'available': len(data) if data else 0
            }
        
        df = pd.DataFrame(data)
        
        # Calculate indicators
        indicators = self.calculate_indicators(symbol, period, ['MA', 'RSI', 'VOLATILITY'])
        
        if self.model_loaded and self.model is not None and self.scaler is not None:
            try:
                # Prepare features
                features = self._prepare_prediction_features(df, indicators)
                X = np.array([list(features.values())])
                
                # Scale features
                X_scaled = self.scaler.transform(X)
                
                # Make prediction
                prediction = self.model.predict(X_scaled)[0]
                probabilities = self.model.predict_proba(X_scaled)[0]
                
                trend = 'UP' if prediction == 1 else 'DOWN'
                confidence = float(max(probabilities))
                
                return {
                    'symbol': symbol.upper(),
                    'trend': trend,
                    'confidence': confidence,
                    'probabilities': {
                        'up': float(probabilities[1]),
                        'down': float(probabilities[0])
                    },
                    'model_version': 'v1.0',
                    'indicators_used': list(features.keys()),
                    'current_price': indicators.get('current_price')
                }
                
            except Exception as e:
                print(f"Error during prediction: {e}")
                return self._fallback_prediction(df, indicators)
        else:
            return self._fallback_prediction(df, indicators)
    
    def _prepare_prediction_features(self, df: pd.DataFrame, indicators: Dict) -> Dict:
        """Prepare features for ML model."""
        # Calculate additional features
        df['MA_5'] = df['close'].rolling(window=5).mean()
        df['MA_20'] = df['close'].rolling(window=20).mean()
        
        # RSI
        rsi = self._calculate_rsi(df['close'])
        
        # Volatility
        volatility = df['close'].pct_change().rolling(window=20).std()
        
        return {
            'MA_5': float(df['MA_5'].iloc[-1]) if not pd.isna(df['MA_5'].iloc[-1]) else indicators.get('MA_5', 0),
            'MA_20': float(df['MA_20'].iloc[-1]) if not pd.isna(df['MA_20'].iloc[-1]) else indicators.get('MA_20', 0),
            'RSI': rsi if rsi else indicators.get('RSI', 50),
            'volatility': float(volatility.iloc[-1]) if not pd.isna(volatility.iloc[-1]) else indicators.get('volatility_daily', 0.01),
        }
    
    def _fallback_prediction(self, df: pd.DataFrame, indicators: Dict) -> Dict:
        """Simple rule-based prediction when ML model is not available."""
        rsi = indicators.get('RSI', 50)
        ma_5 = indicators.get('MA_5')
        ma_20 = indicators.get('MA_20')
        current_price = indicators.get('current_price')
        
        # Simple heuristic
        trend = 'UP'
        confidence = 0.55
        
        if ma_5 and ma_20 and current_price:
            if ma_5 > ma_20 and rsi < 70:
                trend = 'UP'
                confidence = 0.65
            elif ma_5 < ma_20 and rsi > 30:
                trend = 'DOWN'
                confidence = 0.65
            elif rsi > 70:
                trend = 'DOWN'  # Overbought
                confidence = 0.60
            elif rsi < 30:
                trend = 'UP'  # Oversold
                confidence = 0.60
        
        return {
            'symbol': df['close'].name if hasattr(df['close'], 'name') else 'UNKNOWN',
            'trend': trend,
            'confidence': confidence,
            'probabilities': {
                'up': 0.65 if trend == 'UP' else 0.35,
                'down': 0.65 if trend == 'DOWN' else 0.35
            },
            'model_version': 'fallback',
            'note': 'Prédiction basée sur indicateurs techniques (modèle ML non disponible)',
            'indicators': indicators
        }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return None
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None
    
    def _calculate_macd(
        self, 
        prices: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> tuple:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        if len(prices) < slow_period:
            return None, None
        
        ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
        ema_slow = prices.ewm(span=slow_period, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        return float(macd_line.iloc[-1]), float(signal_line.iloc[-1])
    
    def _get_mock_stock_data(self, symbol: str, days: int) -> List[Dict]:
        """Generate mock stock data for development."""
        import random
        random.seed(hash(symbol))
        
        data = []
        base_price = random.uniform(100, 500)
        start_date = datetime.now().date() - timedelta(days=days)
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            
            # Random walk with slight upward bias
            change = random.gauss(0.001, 0.02)  # mean 0.1%, std 2%
            base_price *= (1 + change)
            
            daily_range = base_price * random.uniform(0.01, 0.03)
            
            data.append({
                'date': date.isoformat(),
                'open': round(base_price + random.uniform(-daily_range/2, daily_range/2), 2),
                'high': round(base_price + random.uniform(0, daily_range), 2),
                'low': round(base_price - random.uniform(0, daily_range), 2),
                'close': round(base_price, 2),
                'volume': random.randint(1000000, 10000000)
            })
        
        return data
