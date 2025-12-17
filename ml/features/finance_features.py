"""
Finance Feature Engineering
Extracts features for financial asset trend prediction.
"""

import numpy as np
from typing import Dict, List, Any


class FinanceFeatureExtractor:
    """
    Extracts features from financial asset data for ML prediction.
    
    Features extracted:
    - Price changes (1d, 5d, 10d)
    - Moving averages (MA7, MA20, MA50)
    - Volatility
    - RSI (Relative Strength Index)
    - MACD indicators
    - Momentum
    - Volume trends
    """
    
    MINIMUM_HISTORY = 50  # Minimum price points needed
    
    def __init__(self):
        self.feature_names = None
    
    def extract(self, asset_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract features from asset data.
        
        Args:
            asset_data: Dictionary with price history and volume
            
        Returns:
            Feature array ready for model input
        """
        # Support both 'prices' and 'price_history' keys
        prices = np.array(asset_data.get('prices', asset_data.get('price_history', [])))
        volumes = np.array(asset_data.get('volume', asset_data.get('volume_history', [1] * len(prices))))
        
        if len(prices) == 0:
            raise ValueError("No price data provided")
        
        # Check minimum history requirement
        if len(prices) < self.MINIMUM_HISTORY:
            from utils.exceptions import InsufficientDataError
            raise InsufficientDataError(self.MINIMUM_HISTORY, len(prices))
        
        features = []
        
        # 1. Price changes (returns)
        change_1d = self._percent_change(prices, 1)
        change_5d = self._percent_change(prices, 5)
        change_10d = self._percent_change(prices, 10)
        features.extend([change_1d, change_5d, change_10d])
        
        # 2. Moving averages
        ma7 = self._moving_average(prices, 7)
        ma20 = self._moving_average(prices, 20)
        ma50 = self._moving_average(prices, 50)
        
        current_price = prices[-1]
        ma7_diff = (current_price - ma7) / ma7 if ma7 > 0 else 0
        ma20_diff = (current_price - ma20) / ma20 if ma20 > 0 else 0
        ma50_diff = (current_price - ma50) / ma50 if ma50 > 0 else 0
        features.extend([ma7_diff, ma20_diff, ma50_diff])
        
        # 3. Volatility (standard deviation of returns)
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns[-20:]) if len(returns) >= 20 else np.std(returns)
        features.append(volatility)
        
        # 4. RSI (Relative Strength Index)
        rsi = self._calculate_rsi(prices, period=14)
        rsi_normalized = (rsi - 50) / 50  # Normalize to [-1, 1]
        features.append(rsi_normalized)
        
        # 5. MACD
        macd, signal = self._calculate_macd(prices)
        macd_diff = macd - signal
        features.append(macd_diff)
        
        # 6. Momentum
        momentum_5 = self._momentum(prices, 5)
        momentum_10 = self._momentum(prices, 10)
        features.extend([momentum_5, momentum_10])
        
        # 7. Volume trend
        if len(volumes) >= 20:
            vol_ma = np.mean(volumes[-20:])
            vol_current = volumes[-1]
            vol_trend = (vol_current - vol_ma) / vol_ma if vol_ma > 0 else 0
        else:
            vol_trend = 0.0
        features.append(vol_trend)
        
        # 8. Price position in range
        high_20 = np.max(prices[-20:]) if len(prices) >= 20 else np.max(prices)
        low_20 = np.min(prices[-20:]) if len(prices) >= 20 else np.min(prices)
        if high_20 > low_20:
            price_position = (current_price - low_20) / (high_20 - low_20)
        else:
            price_position = 0.5
        features.append(price_position)
        
        # 9. Trend strength
        trend_strength = self._trend_strength(prices, window=20)
        features.append(trend_strength)
        
        self.feature_names = [
            'change_1d',
            'change_5d',
            'change_10d',
            'ma7_diff',
            'ma20_diff',
            'ma50_diff',
            'volatility',
            'rsi_normalized',
            'macd_diff',
            'momentum_5',
            'momentum_10',
            'volume_trend',
            'price_position',
            'trend_strength'
        ]
        
        return np.array(features).reshape(1, -1)
    
    def _percent_change(self, prices: np.ndarray, period: int) -> float:
        """Calculate percentage change over period."""
        if len(prices) <= period:
            return 0.0
        # Compare current price to price 'period' days ago
        return (prices[-1] - prices[-(period + 1)]) / prices[-(period + 1)]
    
    def _moving_average(self, prices: np.ndarray, window: int) -> float:
        """Calculate moving average."""
        if len(prices) < window:
            return np.mean(prices)
        return np.mean(prices[-window:])
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: np.ndarray) -> tuple:
        """Calculate MACD and signal line."""
        ema12 = self._ema(prices, 12)
        ema26 = self._ema(prices, 26)
        macd = ema12 - ema26
        
        # Signal line would be EMA of MACD, simplified here
        signal = macd * 0.9  # Simplified
        
        return macd, signal
    
    def _ema(self, prices: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return np.mean(prices)
        
        multiplier = 2 / (period + 1)
        ema = prices[-period]
        
        for price in prices[-period+1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _momentum(self, prices: np.ndarray, period: int) -> float:
        """Calculate price momentum."""
        if len(prices) <= period:
            return 0.0
        return (prices[-1] - prices[-period]) / prices[-period]
    
    def _trend_strength(self, prices: np.ndarray, window: int = 20) -> float:
        """Calculate trend strength using linear regression slope."""
        if len(prices) < window:
            window = len(prices)
        
        y = prices[-window:]
        x = np.arange(len(y))
        
        # Simple linear regression
        slope = np.polyfit(x, y, 1)[0]
        
        # Normalize by price
        mean_price = np.mean(y)
        if mean_price > 0:
            normalized_slope = slope / mean_price
        else:
            normalized_slope = 0.0
        
        return normalized_slope
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names in order."""
        if self.feature_names is None:
            return [
                'change_1d',
                'change_5d',
                'change_10d',
                'ma7_diff',
                'ma20_diff',
                'ma50_diff',
                'volatility',
                'rsi_normalized',
                'macd_diff',
                'momentum_5',
                'momentum_10',
                'volume_trend',
                'price_position',
                'trend_strength'
            ]
        return self.feature_names
    
    @staticmethod
    def create_sample_data(trend: str = 'up') -> Dict[str, Any]:
        """
        Create sample asset data for testing.
        
        Args:
            trend: 'up', 'down', or 'neutral'
            
        Returns:
            Sample asset data dictionary
        """
        base_price = 100.0
        days = 60
        
        if trend == 'up':
            prices = base_price + np.cumsum(np.random.randn(days) * 0.5 + 0.3)
        elif trend == 'down':
            prices = base_price + np.cumsum(np.random.randn(days) * 0.5 - 0.3)
        else:  # neutral
            prices = base_price + np.cumsum(np.random.randn(days) * 0.5)
        
        prices = np.maximum(prices, 1.0)  # Ensure positive prices
        volumes = np.random.randint(1000000, 5000000, days)
        
        return {
            'price_history': prices.tolist(),
            'volume_history': volumes.tolist()
        }
