"""
Tests for sports feature extraction.

Validates feature engineering for sports predictions.
"""

import unittest
import numpy as np
import sys
import os

# Add ml directory to path
ml_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ml_dir)

from features.sports_features import SportsFeatureExtractor
from utils.exceptions import MissingFeatureError


class TestSportsFeatureExtractor(unittest.TestCase):
    """Test cases for SportsFeatureExtractor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = SportsFeatureExtractor()
        
        # Sample valid match data
        self.valid_data = {
            'home_form': [2, 1, 2, 1, 2],
            'away_form': [1, 0, 1, 2, 0],
            'home_attack': 75.5,
            'away_attack': 68.2,
            'home_defense': 82.0,
            'away_defense': 78.5,
            'home_goals_scored': 15,
            'away_goals_scored': 12,
            'home_goals_conceded': 8,
            'away_goals_conceded': 10,
            'home_win_rate': 0.65,
            'away_win_rate': 0.50,
            'is_home': True,
            'home_xg': [1.8, 2.1, 1.5, 2.3, 1.9],
            'away_xg': [1.2, 1.5, 1.8, 1.0, 1.6],
            'h2h_history': [1, 1, 0, 1, 2],
            'home_rest_days': 3,
            'away_rest_days': 2
        }
    
    def test_feature_dimensions(self):
        """Test that extracted features have correct shape."""
        features = self.extractor.extract(self.valid_data)
        
        # Should return (1, 10) array
        self.assertEqual(features.shape, (1, 10))
    
    def test_feature_types(self):
        """Test that all features are numeric."""
        features = self.extractor.extract(self.valid_data)
        
        # All values should be float
        self.assertTrue(np.issubdtype(features.dtype, np.number))
        
        # No NaN values
        self.assertFalse(np.any(np.isnan(features)))
        
        # No infinite values
        self.assertFalse(np.any(np.isinf(features)))
    
    def test_required_features(self):
        """Test that all required features are checked."""
        required = self.extractor.REQUIRED_FEATURES
        
        # Should have all required features
        self.assertIn('home_form', required)
        self.assertIn('away_form', required)
        self.assertIn('home_attack', required)
        self.assertIn('away_attack', required)
        self.assertIn('home_defense', required)
        self.assertIn('away_defense', required)
    
    def test_missing_feature_raises_error(self):
        """Test that missing features raise appropriate error."""
        incomplete_data = self.valid_data.copy()
        del incomplete_data['home_attack']
        
        with self.assertRaises(MissingFeatureError):
            self.extractor.extract(incomplete_data)
    
    def test_form_difference_calculation(self):
        """Test form difference feature."""
        features = self.extractor.extract(self.valid_data)
        
        # Form diff should be reasonable
        form_diff = features[0, 0]
        self.assertGreater(form_diff, -5)
        self.assertLess(form_diff, 5)
    
    def test_attack_defense_differences(self):
        """Test attack and defense difference features."""
        features = self.extractor.extract(self.valid_data)
        
        attack_diff = features[0, 1]
        defense_diff = features[0, 2]
        
        # Should reflect differences in ratings
        self.assertGreater(attack_diff, 0)  # Home attack is stronger
        self.assertGreater(defense_diff, 0)  # Home defense is stronger
    
    def test_goal_difference_ratio(self):
        """Test goal difference ratio feature."""
        features = self.extractor.extract(self.valid_data)
        
        goal_ratio = features[0, 3]
        
        # Should be positive (more goals scored than conceded)
        self.assertGreater(goal_ratio, -3)
        self.assertLess(goal_ratio, 3)
    
    def test_home_advantage_flag(self):
        """Test home advantage feature."""
        # Home match
        features_home = self.extractor.extract(self.valid_data)
        self.assertEqual(features_home[0, 5], 1.0)
        
        # Away match
        away_data = self.valid_data.copy()
        away_data['is_home'] = False
        features_away = self.extractor.extract(away_data)
        self.assertEqual(features_away[0, 5], 0.0)
    
    def test_sample_data_generation(self):
        """Test that sample data generator works."""
        sample_data = self.extractor.create_sample_data()
        
        # Should have all required features
        for feature in self.extractor.REQUIRED_FEATURES:
            self.assertIn(feature, sample_data)
        
        # Should be valid for extraction
        features = self.extractor.extract(sample_data)
        self.assertEqual(features.shape, (1, 10))
    
    def test_feature_consistency(self):
        """Test that same input produces same output."""
        features1 = self.extractor.extract(self.valid_data)
        features2 = self.extractor.extract(self.valid_data)
        
        # Should be identical
        np.testing.assert_array_equal(features1, features2)
    
    def test_empty_form_lists(self):
        """Test handling of empty form lists."""
        data_with_empty_form = self.valid_data.copy()
        data_with_empty_form['home_form'] = []
        data_with_empty_form['away_form'] = []
        
        # Should handle gracefully (default to 0)
        features = self.extractor.extract(data_with_empty_form)
        self.assertIsNotNone(features)


if __name__ == '__main__':
    unittest.main()
