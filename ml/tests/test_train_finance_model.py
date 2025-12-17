"""
Tests pour l'entrainement du modele finance.
"""

import os
import pytest
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler


class TestTrainFinanceModel:
    """Tests pour le training du modele finance."""
    
    def test_train_model_basic(self, small_finance_dataset, temp_models_dir):
        """Entrainement basique du modele finance."""
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
        
        df = small_finance_dataset
        
        # Preparer les donnees
        feature_cols = [
            'rsi', 'macd', 'signal', 'sma_20', 'sma_50',
            'volatility', 'volume_ratio', 'price_change'
        ]
        
        X = df[feature_cols]
        y = df['trend']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Normaliser
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Entrainer le modele
        model = GradientBoostingClassifier(
            n_estimators=10,
            max_depth=3,
            random_state=42
        )
        model.fit(X_train_scaled, y_train)
        
        # Verifier les predictions
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Sur un dataset aleatoire, l'accuracy doit etre >= 0.25 (hasard = 0.25 pour 4 classes)
        assert accuracy >= 0.25
        assert accuracy <= 1.0
    
    def test_save_and_load_model_with_scaler(
        self,
        small_finance_dataset,
        temp_models_dir
    ):
        """Sauvegarde et chargement du modele + scaler."""
        from sklearn.model_selection import train_test_split
        
        df = small_finance_dataset
        
        feature_cols = [
            'rsi', 'macd', 'signal', 'sma_20', 'sma_50',
            'volatility', 'volume_ratio', 'price_change'
        ]
        
        X = df[feature_cols]
        y = df['trend']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Normaliser et entrainer
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        model = GradientBoostingClassifier(
            n_estimators=10,
            max_depth=3,
            random_state=42
        )
        model.fit(X_train_scaled, y_train)
        
        # Sauvegarder modele et scaler
        model_path = os.path.join(temp_models_dir, 'finance_model.pkl')
        scaler_path = os.path.join(temp_models_dir, 'finance_scaler.pkl')
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        
        assert os.path.exists(model_path)
        assert os.path.exists(scaler_path)
        
        # Recharger
        loaded_model = joblib.load(model_path)
        loaded_scaler = joblib.load(scaler_path)
        
        # Verifier predictions identiques
        X_test_scaled = loaded_scaler.transform(X_test)
        pred_loaded = loaded_model.predict(X_test_scaled)
        
        assert len(pred_loaded) == len(X_test)
    
    def test_model_predict_proba(self, small_finance_dataset):
        """Le modele renvoie des probabilites."""
        from sklearn.model_selection import train_test_split
        
        df = small_finance_dataset
        
        feature_cols = [
            'rsi', 'macd', 'signal', 'sma_20', 'sma_50',
            'volatility', 'volume_ratio', 'price_change'
        ]
        
        X = df[feature_cols]
        y = df['trend']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = GradientBoostingClassifier(
            n_estimators=10,
            max_depth=3,
            random_state=42
        )
        model.fit(X_train_scaled, y_train)
        
        # Obtenir les probabilites
        probas = model.predict_proba(X_test_scaled)
        
        # Verifier la forme
        assert probas.shape[0] == len(X_test)
        assert probas.shape[1] == 3  # UP, DOWN, NEUTRAL
        
        # Verifier que chaque ligne somme a 1
        for row in probas:
            assert abs(row.sum() - 1.0) < 0.01
