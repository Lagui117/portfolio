"""Train finance trend prediction model using technical indicators.

This script trains a LogisticRegression model to predict stock price trends (UP/DOWN).
Features include moving averages, RSI, MACD, volatility, and price changes.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
import joblib
import os
from datetime import datetime


def calculate_rsi(prices, period=14):
    """Calculate RSI indicator."""
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.zeros(len(prices))
    avg_loss = np.zeros(len(prices))
    
    if len(gains) >= period:
        avg_gain[period] = np.mean(gains[:period])
        avg_loss[period] = np.mean(losses[:period])
        
        for i in range(period + 1, len(prices)):
            avg_gain[i] = (avg_gain[i-1] * (period-1) + gains[i-1]) / period
            avg_loss[i] = (avg_loss[i-1] * (period-1) + losses[i-1]) / period
    
    rs = np.where(avg_loss != 0, avg_gain / avg_loss, 0)
    rsi = 100 - (100 / (1 + rs))
    return rsi[-1] if len(rsi) > 0 else 50


def generate_synthetic_data(n_samples=3000):
    """Generate realistic synthetic stock data."""
    print(f"Generating {n_samples} synthetic samples...")
    np.random.seed(42)
    data = []
    
    for _ in range(n_samples):
        # Simulate price history
        days = 100
        base = np.random.uniform(20, 500)
        trend = np.random.choice(['UP', 'DOWN'], p=[0.5, 0.5])
        drift = np.random.uniform(0.001, 0.005) if trend == 'UP' else np.random.uniform(-0.005, -0.001)
        vol = np.random.uniform(0.015, 0.035)
        
        prices = [base]
        for _ in range(days - 1):
            prices.append(prices[-1] * (1 + drift + np.random.normal(0, vol)))
        
        prices = np.array(prices)
        
        # Calculate indicators
        ma_5 = np.mean(prices[-5:])
        ma_20 = np.mean(prices[-20:])
        ma_50 = np.mean(prices[-50:])
        rsi = calculate_rsi(prices)
        
        ema_12 = pd.Series(prices).ewm(span=12).mean().iloc[-1]
        ema_26 = pd.Series(prices).ewm(span=26).mean().iloc[-1]
        macd = ema_12 - ema_26
        
        returns = np.diff(prices) / prices[:-1]
        vol_daily = np.std(returns[-20:])
        vol_annual = vol_daily * np.sqrt(252)
        
        chg_1d = (prices[-1] - prices[-2]) / prices[-2]
        chg_5d = (prices[-1] - prices[-6]) / prices[-6]
        chg_20d = (prices[-1] - prices[-21]) / prices[-21]
        
        # Future trend
        future = []
        for _ in range(5):
            future.append(prices[-1] * (1 + drift + np.random.normal(0, vol)))
        target = 'UP' if np.mean(future) > prices[-1] else 'DOWN'
        
        data.append({
            'MA_5': ma_5,
            'MA_20': ma_20,
            'MA_50': ma_50,
            'RSI': rsi,
            'MACD': macd,
            'volatility_daily': vol_daily,
            'volatility_annual': vol_annual,
            'price_change_1d': chg_1d,
            'price_change_5d': chg_5d,
            'price_change_20d': chg_20d,
            'ma5_minus_ma20': ma_5 - ma_20,
            'ma20_minus_ma50': ma_20 - ma_50,
            'ma5_ratio': ma_5 / prices[-1],
            'ma20_ratio': ma_20 / prices[-1],
            'trend': target
        })
    
    df = pd.DataFrame(data)
    print(f"✓ Generated: {df.shape}")
    print(f"  Trends: {df['trend'].value_counts().to_dict()}")
    return df


def train_finance_model():
    """Train and save finance prediction model."""
    
    print("\n" + "="*60)
    print("FINANCE PREDICTION MODEL TRAINING")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Generate data
    df = generate_synthetic_data(n_samples=3000)
    
    # Prepare
    X = df.drop('trend', axis=1)
    y = df['trend']
    
    print(f"\nFeatures: {list(X.columns)[:5]}...")
    print(f"Classes: {y.unique()}")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nTrain: {len(X_train)} | Test: {len(X_test)}")
    
    # Scale
    print("\nScaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("✓ Scaled")
    
    # Train
    print("\nTraining LogisticRegression...")
    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train_scaled, y_train)
    print("✓ Trained")
    
    # Cross-validation
    print("\n5-fold cross-validation...")
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
    print(f"CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
    
    # Test
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nTest Accuracy: {accuracy:.3f}")
    try:
        auc = roc_auc_score(y_test, y_proba[:, 1])
        print(f"ROC AUC: {auc:.3f}")
    except:
        pass
    
    print("\n" + "="*60)
    print("CLASSIFICATION REPORT")
    print("="*60)
    print(classification_report(y_test, y_pred))
    
    # Coefficients
    print("\nTop 10 Coefficients:")
    coefs = pd.DataFrame({
        'feature': X.columns,
        'coef': model.coef_[0]
    })
    coefs['abs'] = coefs['coef'].abs()
    for _, row in coefs.sort_values('abs', ascending=False).head(10).iterrows():
        print(f"  {row['feature']:30s}: {row['coef']:+.4f}")
    
    # Save
    model_dir = '../models'
    os.makedirs(model_dir, exist_ok=True)
    
    joblib.dump(model, f'{model_dir}/finance_model.pkl')
    joblib.dump(scaler, f'{model_dir}/finance_scaler.pkl')
    
    print(f"\n✅ Model saved: {model_dir}/finance_model.pkl")
    print(f"✅ Scaler saved: {model_dir}/finance_scaler.pkl")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return model, scaler


if __name__ == '__main__':
    train_finance_model()
