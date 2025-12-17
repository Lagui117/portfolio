"""
Sample data generation for testing.

Creates CSV files with realistic sports and finance data.
"""

import os
import pandas as pd
import numpy as np


def generate_sports_sample_data(n_samples=100):
    """
    Generate sample sports match data.
    
    Args:
        n_samples: Number of matches to generate
        
    Returns:
        DataFrame with match statistics
    """
    np.random.seed(42)
    
    data = {
        # Team ratings (60-90 range)
        'home_attack': np.random.uniform(60, 90, n_samples),
        'away_attack': np.random.uniform(60, 90, n_samples),
        'home_defense': np.random.uniform(60, 90, n_samples),
        'away_defense': np.random.uniform(60, 90, n_samples),
        
        # Goals statistics
        'home_goals_scored': np.random.randint(8, 25, n_samples),
        'away_goals_scored': np.random.randint(8, 25, n_samples),
        'home_goals_conceded': np.random.randint(5, 20, n_samples),
        'away_goals_conceded': np.random.randint(5, 20, n_samples),
        
        # Win rates
        'home_win_rate': np.random.uniform(0.3, 0.8, n_samples),
        'away_win_rate': np.random.uniform(0.3, 0.8, n_samples),
        
        # Match context
        'is_home': np.random.choice([True, False], n_samples),
        'home_rest_days': np.random.randint(2, 7, n_samples),
        'away_rest_days': np.random.randint(2, 7, n_samples),
    }
    
    # Generate form (list of results)
    data['home_form'] = [
        ','.join([str(np.random.randint(0, 3)) for _ in range(5)])
        for _ in range(n_samples)
    ]
    data['away_form'] = [
        ','.join([str(np.random.randint(0, 3)) for _ in range(5)])
        for _ in range(n_samples)
    ]
    
    # Generate xG (expected goals)
    data['home_xg'] = [
        ','.join([f"{np.random.uniform(0.5, 3.0):.2f}" for _ in range(5)])
        for _ in range(n_samples)
    ]
    data['away_xg'] = [
        ','.join([f"{np.random.uniform(0.5, 3.0):.2f}" for _ in range(5)])
        for _ in range(n_samples)
    ]
    
    # Generate head-to-head history
    data['h2h_history'] = [
        ','.join([str(np.random.randint(0, 3)) for _ in range(5)])
        for _ in range(n_samples)
    ]
    
    # Generate outcomes based on features (simulated)
    outcomes = []
    for i in range(n_samples):
        # Simple rule-based outcome for realistic distribution
        home_strength = data['home_attack'][i] + data['home_defense'][i]
        away_strength = data['away_attack'][i] + data['away_defense'][i]
        
        diff = home_strength - away_strength
        
        if diff > 10:
            outcome = np.random.choice([0, 1, 2], p=[0.6, 0.25, 0.15])
        elif diff < -10:
            outcome = np.random.choice([0, 1, 2], p=[0.15, 0.25, 0.6])
        else:
            outcome = np.random.choice([0, 1, 2], p=[0.4, 0.3, 0.3])
        
        outcomes.append(outcome)
    
    data['outcome'] = outcomes  # 0=Home, 1=Draw, 2=Away
    
    return pd.DataFrame(data)


def generate_finance_sample_data(n_samples=100):
    """
    Generate sample financial asset data.
    
    Args:
        n_samples: Number of assets/time periods to generate
        
    Returns:
        DataFrame with price and volume history
    """
    np.random.seed(42)
    
    data_rows = []
    
    for i in range(n_samples):
        # Generate price series (60 points)
        base_price = np.random.uniform(50, 500)
        trend = np.random.choice([-1, 0, 1], p=[0.3, 0.3, 0.4])
        
        prices = [base_price]
        for j in range(59):
            # Random walk with trend
            change = np.random.randn() * 2 + (trend * 0.5)
            new_price = prices[-1] + change
            prices.append(max(new_price, 1))  # Avoid negative prices
        
        # Generate volume series
        base_volume = np.random.randint(1000, 50000)
        volumes = [
            int(base_volume + np.random.randn() * base_volume * 0.2)
            for _ in range(60)
        ]
        
        # Determine trend class based on price change
        price_change = ((prices[-1] - prices[0]) / prices[0]) * 100
        
        if price_change > 5:
            trend_class = 0  # UP
        elif price_change < -5:
            trend_class = 2  # DOWN
        else:
            trend_class = 1  # NEUTRAL
        
        data_rows.append({
            'asset_id': f'ASSET_{i:03d}',
            'price_history': ','.join([f"{p:.2f}" for p in prices]),
            'volume_history': ','.join([str(v) for v in volumes]),
            'trend': trend_class
        })
    
    return pd.DataFrame(data_rows)


def save_sample_data():
    """Generate and save sample data to CSV files."""
    # Create data directory
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate sports data
    sports_df = generate_sports_sample_data(100)
    sports_path = os.path.join(data_dir, 'sports_sample.csv')
    sports_df.to_csv(sports_path, index=False)
    print(f"✓ Sports sample data saved to {sports_path}")
    print(f"  Samples: {len(sports_df)}")
    print(f"  Columns: {list(sports_df.columns)}")
    print()
    
    # Generate finance data
    finance_df = generate_finance_sample_data(100)
    finance_path = os.path.join(data_dir, 'finance_sample.csv')
    finance_df.to_csv(finance_path, index=False)
    print(f"✓ Finance sample data saved to {finance_path}")
    print(f"  Samples: {len(finance_df)}")
    print(f"  Columns: {list(finance_df.columns)}")
    print()
    
    # Print sample rows
    print("Sports data sample:")
    print(sports_df.head(3))
    print()
    
    print("Finance data sample:")
    print(finance_df.head(3))


if __name__ == '__main__':
    save_sample_data()
