"""
Evaluate trained ML models.

This script loads trained models and evaluates their performance on test data.
Displays detailed metrics: accuracy, precision, recall, F1-score, confusion matrix.
"""
import os
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from datetime import datetime

# Paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
SPORTS_MODEL_PATH = os.path.join(MODEL_DIR, 'sports_model.pkl')
FINANCE_MODEL_PATH = os.path.join(MODEL_DIR, 'finance_model.pkl')
FINANCE_SCALER_PATH = os.path.join(MODEL_DIR, 'finance_scaler.pkl')


def print_header(title):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def evaluate_sports_model():
    """Evaluate sports prediction model."""
    print_header("SPORTS MODEL EVALUATION")
    
    if not os.path.exists(SPORTS_MODEL_PATH):
        print("❌ Sports model not found. Run train_sports_model.py first.")
        return
    
    # Load model
    print(f"\n📂 Loading model from: {SPORTS_MODEL_PATH}")
    model = joblib.load(SPORTS_MODEL_PATH)
    print(f"✓ Model loaded: {type(model).__name__}")
    
    # Generate test data (same distribution as training)
    print("\n📊 Generating test dataset...")
    np.random.seed(123)  # Different seed for test data
    n_test = 1000
    
    test_data = []
    for _ in range(n_test):
        home_win_rate = np.random.uniform(0.2, 0.8)
        away_win_rate = np.random.uniform(0.2, 0.8)
        home_form = np.random.uniform(0, 3)
        away_form = np.random.uniform(0, 3)
        
        strength_diff = home_win_rate - away_win_rate
        home_odds = max(1.1, 4.0 - strength_diff * 2 + np.random.normal(0, 0.3))
        draw_odds = np.random.uniform(2.8, 4.5)
        away_odds = max(1.1, 4.0 + strength_diff * 2 + np.random.normal(0, 0.3))
        
        prob = np.random.random()
        home_prob = 0.4 + strength_diff * 0.3
        if prob < home_prob:
            outcome = 'HOME_WIN'
        elif prob < home_prob + 0.25:
            outcome = 'DRAW'
        else:
            outcome = 'AWAY_WIN'
        
        test_data.append({
            'home_win_rate': home_win_rate,
            'home_avg_goals_scored': np.random.uniform(0.5, 3.0),
            'home_recent_form': home_form,
            'away_win_rate': away_win_rate,
            'away_avg_goals_scored': np.random.uniform(0.5, 3.0),
            'away_recent_form': away_form,
            'win_rate_diff': home_win_rate - away_win_rate,
            'form_diff': home_form - away_form,
            'h2h_home_win_rate': np.random.randint(0, 10) / max(np.random.randint(5, 20), 1),
            'home_odds': home_odds,
            'draw_odds': draw_odds,
            'away_odds': away_odds,
            'odds_ratio': home_odds / away_odds,
            'outcome': outcome
        })
    
    df_test = pd.DataFrame(test_data)
    X_test = df_test.drop('outcome', axis=1)
    y_test = df_test['outcome']
    
    print(f"✓ Test dataset: {X_test.shape[0]} samples, {X_test.shape[1]} features")
    
    # Predictions
    print("\n🔮 Making predictions...")
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    
    # Metrics
    print("\n" + "="*70)
    print("  PERFORMANCE METRICS")
    print("="*70)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n📊 Overall Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    # Per-class metrics
    classes = model.classes_
    precision = precision_score(y_test, y_pred, average=None, labels=classes, zero_division=0)
    recall = recall_score(y_test, y_pred, average=None, labels=classes, zero_division=0)
    f1 = f1_score(y_test, y_pred, average=None, labels=classes, zero_division=0)
    
    print("\n📈 Per-Class Metrics:")
    print(f"{'Class':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
    print("-" * 55)
    for i, cls in enumerate(classes):
        print(f"{cls:<15} {precision[i]:<12.4f} {recall[i]:<12.4f} {f1[i]:<12.4f}")
    
    # Weighted averages
    precision_avg = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall_avg = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1_avg = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    print("\n📊 Weighted Averages:")
    print(f"  Precision: {precision_avg:.4f}")
    print(f"  Recall:    {recall_avg:.4f}")
    print(f"  F1-Score:  {f1_avg:.4f}")
    
    # Confusion Matrix
    print("\n📋 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred, labels=classes)
    print(f"\n{'':>15}", end='')
    for cls in classes:
        print(f"{cls:<12}", end='')
    print()
    print("-" * (15 + 12 * len(classes)))
    for i, cls in enumerate(classes):
        print(f"{cls:>15}", end='')
        for j in range(len(classes)):
            print(f"{cm[i][j]:<12}", end='')
        print()
    
    # Classification Report
    print("\n" + "="*70)
    print("  DETAILED CLASSIFICATION REPORT")
    print("="*70)
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # Sample predictions
    print("\n" + "="*70)
    print("  SAMPLE PREDICTIONS (First 5)")
    print("="*70)
    for i in range(min(5, len(y_test))):
        print(f"\nSample {i+1}:")
        print(f"  True:      {y_test.iloc[i]}")
        print(f"  Predicted: {y_pred[i]}")
        print(f"  Probabilities: ", end='')
        for j, cls in enumerate(classes):
            print(f"{cls}: {y_proba[i][j]:.3f} ", end='')
        print()
    
    return {
        'accuracy': accuracy,
        'precision': precision_avg,
        'recall': recall_avg,
        'f1_score': f1_avg
    }


def evaluate_finance_model():
    """Evaluate finance prediction model."""
    print_header("FINANCE MODEL EVALUATION")
    
    if not os.path.exists(FINANCE_MODEL_PATH):
        print("❌ Finance model not found. Run train_finance_model.py first.")
        return
    
    # Load model and scaler
    print(f"\n📂 Loading model from: {FINANCE_MODEL_PATH}")
    model = joblib.load(FINANCE_MODEL_PATH)
    print(f"✓ Model loaded: {type(model).__name__}")
    
    print(f"\n📂 Loading scaler from: {FINANCE_SCALER_PATH}")
    scaler = joblib.load(FINANCE_SCALER_PATH)
    print(f"✓ Scaler loaded: {type(scaler).__name__}")
    
    # Generate test data
    print("\n📊 Generating test dataset...")
    np.random.seed(456)  # Different seed
    n_test = 600
    
    test_data = []
    for _ in range(n_test):
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
        
        # Simple RSI calculation
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else 0
        avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else 0
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        
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
        
        test_data.append({
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
    
    df_test = pd.DataFrame(test_data)
    X_test = df_test.drop('trend', axis=1)
    y_test = df_test['trend']
    
    print(f"✓ Test dataset: {X_test.shape[0]} samples, {X_test.shape[1]} features")
    
    # Scale features
    print("\n⚙️ Scaling features...")
    X_test_scaled = scaler.transform(X_test)
    
    # Predictions
    print("\n🔮 Making predictions...")
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)
    
    # Metrics
    print("\n" + "="*70)
    print("  PERFORMANCE METRICS")
    print("="*70)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n📊 Overall Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    # Binary classification metrics
    classes = model.classes_
    precision = precision_score(y_test, y_pred, average='binary', pos_label='UP', zero_division=0)
    recall = recall_score(y_test, y_pred, average='binary', pos_label='UP', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='binary', pos_label='UP', zero_division=0)
    
    print("\n📈 Binary Classification Metrics (UP class):")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")
    
    # ROC AUC
    try:
        from sklearn.metrics import roc_auc_score
        roc_auc = roc_auc_score(y_test, y_proba[:, 1])
        print(f"\n📊 ROC AUC Score: {roc_auc:.4f}")
    except:
        print("\n📊 ROC AUC Score: N/A")
    
    # Confusion Matrix
    print("\n📋 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred, labels=classes)
    print(f"\n{'':>15}", end='')
    for cls in classes:
        print(f"{cls:<12}", end='')
    print()
    print("-" * (15 + 12 * len(classes)))
    for i, cls in enumerate(classes):
        print(f"{cls:>15}", end='')
        for j in range(len(classes)):
            print(f"{cm[i][j]:<12}", end='')
        print()
    
    # Classification Report
    print("\n" + "="*70)
    print("  DETAILED CLASSIFICATION REPORT")
    print("="*70)
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # Feature importance (coefficients)
    print("\n" + "="*70)
    print("  TOP 10 MOST IMPORTANT FEATURES")
    print("="*70)
    feature_importance = pd.DataFrame({
        'feature': X_test.columns,
        'coefficient': model.coef_[0]
    })
    feature_importance['abs_coef'] = feature_importance['coefficient'].abs()
    feature_importance = feature_importance.sort_values('abs_coef', ascending=False)
    
    for idx, row in feature_importance.head(10).iterrows():
        direction = "↗️ Bullish" if row['coefficient'] > 0 else "↘️ Bearish"
        print(f"  {row['feature']:25s}: {row['coefficient']:+.4f}  {direction}")
    
    # Sample predictions
    print("\n" + "="*70)
    print("  SAMPLE PREDICTIONS (First 5)")
    print("="*70)
    for i in range(min(5, len(y_test))):
        print(f"\nSample {i+1}:")
        print(f"  True:      {y_test.iloc[i]}")
        print(f"  Predicted: {y_pred[i]}")
        print(f"  Probabilities: DOWN: {y_proba[i][0]:.3f}, UP: {y_proba[i][1]:.3f}")
        print(f"  Confidence: {max(y_proba[i]):.3f}")
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }


def main():
    """Main evaluation pipeline."""
    print("\n" + "="*70)
    print("  PREDICTWISE ML MODELS EVALUATION")
    print("="*70)
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = {}
    
    # Evaluate sports model
    try:
        sports_metrics = evaluate_sports_model()
        if sports_metrics:
            results['sports'] = sports_metrics
    except Exception as e:
        print(f"\n❌ Error evaluating sports model: {e}")
    
    print("\n\n")
    
    # Evaluate finance model
    try:
        finance_metrics = evaluate_finance_model()
        if finance_metrics:
            results['finance'] = finance_metrics
    except Exception as e:
        print(f"\n❌ Error evaluating finance model: {e}")
    
    # Summary
    if results:
        print("\n" + "="*70)
        print("  EVALUATION SUMMARY")
        print("="*70)
        
        if 'sports' in results:
            print("\n🏆 Sports Model:")
            print(f"  Accuracy:  {results['sports']['accuracy']:.4f}")
            print(f"  Precision: {results['sports']['precision']:.4f}")
            print(f"  Recall:    {results['sports']['recall']:.4f}")
            print(f"  F1-Score:  {results['sports']['f1_score']:.4f}")
        
        if 'finance' in results:
            print("\n💰 Finance Model:")
            print(f"  Accuracy:  {results['finance']['accuracy']:.4f}")
            print(f"  Precision: {results['finance']['precision']:.4f}")
            print(f"  Recall:    {results['finance']['recall']:.4f}")
            print(f"  F1-Score:  {results['finance']['f1_score']:.4f}")
        
        print("\n" + "="*70)
        print("  ⚠️  DISCLAIMER")
        print("="*70)
        print("  These models are for EDUCATIONAL PURPOSES ONLY.")
        print("  Do not use for real betting or financial decisions.")
        print("  Past performance does not guarantee future results.")
        print("="*70)
    
    print("\n✅ Evaluation completed!\n")


if __name__ == '__main__':
    main()
