"""
Tests for finance feature extraction.

Validates feature engineering for financial predictions.
"""

import unittest
import numpy as np
import sys
import os

# Add ml directory to path
ml_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ml_dir)

from features.finance_features import FinanceFeatureExtractor
from utils.exceptions import InsufficientDataError


class TestFinanceFeatureExtractor(unittest.TestCase):
    """Test cases for FinanceFeatureExtractor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = FinanceFeatureExtractor()
        
        # Generate valid price history (50+ points)
        np.random.seed(42)
        base_price = 100.0
        prices = [base_price]
        
        for _ in range(59):
            change = np.random.randn() * 2
            prices.append(prices[-1] + change)
        
        self.valid_data = {
            'price_history': prices,
            'volume_history': np.random.randint(1000, 10000, size=60).tolist()
        }
    
    def test_feature_dimensions(self):
        """Test that extracted features have correct shape."""
        features = self.extractor.extract(self.valid_data)
        
        # Should return (1, 14) array
        self.assertEqual(features.shape, (1, 14))
    
    def test_feature_types(self):
        """Test that all features are numeric."""
        features = self.extractor.extract(self.valid_data)
        
        # All values should be float
        self.assertTrue(np.issubdtype(features.dtype, np.number))
        
        # No NaN values
        self.assertFalse(np.any(np.isnan(features)))
        
        # No infinite values
        self.assertFalse(np.any(np.isinf(features)))
    
    def test_minimum_history_requirement(self):
        """Test that insufficient data raises error."""
        short_data = {
            'price_history': [100, 101, 102],
            'volume_history': [1000, 1100, 1200]
        }
        
        with self.assertRaises(InsufficientDataError):
            self.extractor.extract(short_data)
    
    def test_price_changes_calculation(self):
        """Test percentage change features."""
        features = self.extractor.extract(self.valid_data)
        
        change_1d = features[0, 0]
        change_5d = features[0, 1]
        change_10d = features[0, 2]
        
        # All changes should be reasonable percentages
        for change in [change_1d, change_5d, change_10d]:
            self.assertGreater(change, -50)  # Not more than -50%
            self.assertLess(change, 50)      # Not more than +50%
    
    def test_moving_average_differences(self):
        """Test moving average difference features."""
        features = self.extractor.extract(self.valid_data)
        
        ma7_diff = features[0, 3]
        ma20_diff = features[0, 4]
        ma50_diff = features[0, 5]
        
        # All should be percentage differences
        for diff in [ma7_diff, ma20_diff, ma50_diff]:
            self.assertGreater(diff, -30)
            self.assertLess(diff, 30)
    
    def test_volatility_calculation(self):
        """Test volatility feature."""
        features = self.extractor.extract(self.valid_data)
        
        volatility = features[0, 6]
        
        # Volatility should be non-negative
        self.assertGreaterEqual(volatility, 0)
        
        # Should be reasonable (not extremely high)
        self.assertLess(volatility, 100)
    
    def test_rsi_calculation(self):
        """Test RSI indicator."""
        features = self.extractor.extract(self.valid_data)
        
        rsi = features[0, 7]
        
        # RSI should be normalized between -1 and 1
        self.assertGreaterEqual(rsi, -1)
        self.assertLessEqual(rsi, 1)
    
    def test_macd_calculation(self):
        """Test MACD indicator."""
        features = self.extractor.extract(self.valid_data)
        
        macd_diff = features[0, 8]
        
        # MACD should be reasonable
        self.assertGreater(macd_diff, -10)
        self.assertLess(macd_diff, 10)
    
    def test_momentum_features(self):
        """Test momentum indicators."""
        features = self.extractor.extract(self.valid_data)
        
        momentum_5 = features[0, 9]
        momentum_10 = features[0, 10]
        
        # Momentum should be percentage changes
        for momentum in [momentum_5, momentum_10]:
            self.assertGreater(momentum, -50)
            self.assertLess(momentum, 50)
    
    def test_volume_trend(self):
        """Test volume trend feature."""
        features = self.extractor.extract(self.valid_data)
        
        volume_trend = features[0, 11]
        
        # Volume trend should be reasonable
        self.assertGreater(volume_trend, -10)
        self.assertLess(volume_trend, 10)
    
    def test_price_position(self):
        """Test price position feature."""
        features = self.extractor.extract(self.valid_data)
        
        price_position = features[0, 12]
        
        # Should be between 0 and 100
        self.assertGreaterEqual(price_position, 0)
        self.assertLessEqual(price_position, 100)
    
    def test_trend_strength(self):
        """Test trend strength feature."""
        features = self.extractor.extract(self.valid_data)
        
        trend_strength = features[0, 13]
        
        # Should be between -100 and 100
        self.assertGreaterEqual(trend_strength, -100)
        self.assertLessEqual(trend_strength, 100)
    
    def test_sample_data_generation(self):
        """Test that sample data generator works."""
        sample_data = self.extractor.create_sample_data()
        
        # Should have required fields
        self.assertIn('price_history', sample_data)
        self.assertIn('volume_history', sample_data)
        
        # Should have enough data points
        self.assertGreaterEqual(
            len(sample_data['price_history']),
            self.extractor.MINIMUM_HISTORY
        )
        
        # Should be valid for extraction
        features = self.extractor.extract(sample_data)
        self.assertEqual(features.shape, (1, 14))
    
    def test_feature_consistency(self):
        """Test that same input produces same output."""
        features1 = self.extractor.extract(self.valid_data)
        features2 = self.extractor.extract(self.valid_data)
        
        # Should be identical
        np.testing.assert_array_equal(features1, features2)
    
    def test_uptrend_scenario(self):
        """Test feature extraction on uptrending data."""
        uptrend_data = {
            'price_history': list(range(100, 160)),  # 60 points, linear uptrend
            'volume_history': [5000] * 60
        }
        
        features = self.extractor.extract(uptrend_data)
        
        # All changes should be positive
        self.assertGreater(features[0, 0], 0)  # 1-day change
        self.assertGreater(features[0, 1], 0)  # 5-day change
        self.assertGreater(features[0, 2], 0)  # 10-day change
    
    def test_downtrend_scenario(self):
        """Test feature extraction on downtrending data."""
        downtrend_data = {
            'price_history': list(range(160, 100, -1)),  # 60 points, linear downtrend
            'volume_history': [5000] * 60
        }
        
        features = self.extractor.extract(downtrend_data)
        
        # All changes should be negative
        self.assertLess(features[0, 0], 0)  # 1-day change
        self.assertLess(features[0, 1], 0)  # 5-day change
        self.assertLess(features[0, 2], 0)  # 10-day change


if __name__ == '__main__':
    unittest.main()
