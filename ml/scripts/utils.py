"""ML utilities and data preprocessing."""
import pandas as pd
import numpy as np


def load_sports_data(filepath: str) -> pd.DataFrame:
    """Load sports data from CSV file."""
    return pd.read_csv(filepath)


def prepare_sports_features(df: pd.DataFrame) -> tuple:
    """
    Prepare features for sports prediction model.
    
    Returns:
        X: Feature matrix
        y: Target variable
    """
    # Note: Cette fonction est un placeholder pour l'intégration future de données réelles
    # Pour l'instant, les scripts d'entraînement génèrent leurs propres données synthétiques
    
    if df is None or df.empty:
        raise ValueError("DataFrame vide ou None fourni")
    
    # Features basiques (à adapter selon vos données réelles)
    feature_columns = ['home_win_rate', 'away_win_rate', 'home_form', 'away_form']
    target_column = 'outcome'
    
    if not all(col in df.columns for col in feature_columns + [target_column]):
        raise ValueError(f"Colonnes manquantes. Attendu: {feature_columns + [target_column]}")
    
    X = df[feature_columns]
    y = df[target_column]
    
    return X, y


def load_finance_data(filepath: str) -> pd.DataFrame:
    """Load finance data from CSV file."""
    return pd.read_csv(filepath)


def prepare_finance_features(df: pd.DataFrame) -> tuple:
    """
    Prepare features for finance prediction model.
    
    Returns:
        X: Feature matrix
        y: Target variable (UP/DOWN)
    """
    # Calculate technical indicators
    df['MA_5'] = df['close'].rolling(window=5).mean()
    df['MA_20'] = df['close'].rolling(window=20).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Volatility
    df['volatility'] = df['close'].pct_change().rolling(window=20).std()
    
    # Target: next day price movement
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    
    # Drop NaN
    df = df.dropna()
    
    feature_cols = ['MA_5', 'MA_20', 'RSI', 'volatility']
    X = df[feature_cols]
    y = df['target']
    
    return X, y


def evaluate_model(y_true, y_pred):
    """Evaluate model performance."""
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='weighted'),
        'recall': recall_score(y_true, y_pred, average='weighted'),
        'f1': f1_score(y_true, y_pred, average='weighted')
    }
    
    return metrics
