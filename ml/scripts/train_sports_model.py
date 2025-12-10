"""Train sports prediction model using historical match data.

This script trains a RandomForestClassifier to predict match outcomes (HOME_WIN, DRAW, AWAY_WIN).
Features include team statistics, recent form, head-to-head records, and odds.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
from datetime import datetime


def generate_synthetic_data(n_samples=5000):
    """Generate realistic synthetic sports data."""
    print(f"Generating {n_samples} synthetic training samples...")
    np.random.seed(42)
    data = []
    
    for _ in range(n_samples):
        # Home team stats
        home_win_rate = np.random.uniform(0.2, 0.8)
        home_avg_goals = np.random.uniform(0.5, 3.0)
        home_form = np.random.uniform(0, 3)
        
        # Away team stats
        away_win_rate = np.random.uniform(0.2, 0.8)
        away_avg_goals = np.random.uniform(0.5, 3.0)
        away_form = np.random.uniform(0, 3)
        
        # H2H
        h2h_wins = np.random.randint(0, 10)
        h2h_total = np.random.randint(max(h2h_wins, 5), 20)
        
        # Odds
        strength_diff = home_win_rate - away_win_rate
        home_odds = max(1.1, 4.0 - strength_diff * 2 + np.random.normal(0, 0.3))
        draw_odds = np.random.uniform(2.8, 4.5)
        away_odds = max(1.1, 4.0 + strength_diff * 2 + np.random.normal(0, 0.3))
        
        # Outcome based on strength
        prob = np.random.random()
        home_prob = 0.4 + strength_diff * 0.3
        if prob < home_prob:
            outcome = 'HOME_WIN'
        elif prob < home_prob + 0.25:
            outcome = 'DRAW'
        else:
            outcome = 'AWAY_WIN'
        
        data.append({
            'home_win_rate': home_win_rate,
            'home_avg_goals_scored': home_avg_goals,
            'home_recent_form': home_form,
            'away_win_rate': away_win_rate,
            'away_avg_goals_scored': away_avg_goals,
            'away_recent_form': away_form,
            'win_rate_diff': home_win_rate - away_win_rate,
            'form_diff': home_form - away_form,
            'h2h_home_win_rate': h2h_wins / max(h2h_total, 1),
            'home_odds': home_odds,
            'draw_odds': draw_odds,
            'away_odds': away_odds,
            'odds_ratio': home_odds / away_odds,
            'outcome': outcome
        })
    
    df = pd.DataFrame(data)
    print(f"✓ Generated dataset: {df.shape}")
    print(f"  Outcomes: {df['outcome'].value_counts().to_dict()}")
    return df


def train_sports_model():
    """Train and save sports prediction model."""
    
    print("\n" + "="*60)
    print("SPORTS PREDICTION MODEL TRAINING")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Generate data
    df = generate_synthetic_data(n_samples=5000)
    
    # Prepare features
    X = df.drop('outcome', axis=1)
    y = df['outcome']
    
    print(f"\nFeatures: {list(X.columns)[:5]}...")
    print(f"Classes: {y.unique()}")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nTrain: {len(X_train)} | Test: {len(X_test)}")
    
    # Train
    print("\nTraining RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    print("✓ Trained")
    
    # Cross-validation
    print("\n5-fold cross-validation...")
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
    print(f"CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
    
    # Test
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy: {accuracy:.3f}")
    
    print("\n" + "="*60)
    print("CLASSIFICATION REPORT")
    print("="*60)
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    print("\nTop 10 Features:")
    feat_imp = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    for _, row in feat_imp.head(10).iterrows():
        print(f"  {row['feature']:30s}: {row['importance']:.4f}")
    
    # Save
    model_path = '../models/sports_model.pkl'
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    
    print(f"\n✅ Model saved: {model_path}")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return model


if __name__ == '__main__':
    train_sports_model()
