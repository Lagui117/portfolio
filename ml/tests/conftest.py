"""
Configuration pytest et fixtures pour les tests ML.
"""

import os
import sys
import tempfile
import numpy as np
import pandas as pd
import pytest

# Ajouter ml/ au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def temp_models_dir():
    """Repertoire temporaire pour les modeles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def small_sports_dataset():
    """Petit dataset sports pour tests."""
    np.random.seed(42)
    
    n_samples = 100
    
    data = {
        'home_win_rate': np.random.uniform(0.3, 0.8, n_samples),
        'away_win_rate': np.random.uniform(0.3, 0.8, n_samples),
        'home_goals_avg': np.random.uniform(1.0, 3.0, n_samples),
        'away_goals_avg': np.random.uniform(1.0, 3.0, n_samples),
        'home_odds': np.random.uniform(1.5, 4.0, n_samples),
        'draw_odds': np.random.uniform(2.5, 4.5, n_samples),
        'away_odds': np.random.uniform(1.5, 4.0, n_samples),
        'result': np.random.choice(['home', 'draw', 'away'], n_samples)
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def small_finance_dataset():
    """Petit dataset finance pour tests."""
    np.random.seed(42)
    
    n_samples = 100
    
    data = {
        'rsi': np.random.uniform(20, 80, n_samples),
        'macd': np.random.uniform(-2, 2, n_samples),
        'signal': np.random.uniform(-2, 2, n_samples),
        'sma_20': np.random.uniform(90, 110, n_samples),
        'sma_50': np.random.uniform(85, 115, n_samples),
        'volatility': np.random.uniform(0.01, 0.05, n_samples),
        'volume_ratio': np.random.uniform(0.5, 2.0, n_samples),
        'price_change': np.random.uniform(-0.05, 0.05, n_samples),
        'trend': np.random.choice(['UP', 'DOWN', 'NEUTRAL'], n_samples)
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_match_features():
    """Features d'un match pour prediction."""
    return {
        'home_win_rate': 0.65,
        'away_win_rate': 0.45,
        'home_goals_avg': 2.1,
        'away_goals_avg': 1.5,
        'home_odds': 1.85,
        'draw_odds': 3.40,
        'away_odds': 4.50
    }


@pytest.fixture
def sample_stock_features():
    """Features d'un actif pour prediction."""
    return {
        'rsi': 58.5,
        'macd': 1.2,
        'signal': 0.9,
        'sma_20': 182.0,
        'sma_50': 178.5,
        'volatility': 0.025,
        'volume_ratio': 1.15,
        'price_change': 0.02
    }
