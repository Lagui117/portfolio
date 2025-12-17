"""
Tests pour l'entrainement du modele sports.
"""

import os
import pytest
import joblib
from sklearn.ensemble import RandomForestClassifier


class TestTrainSportsModel:
    """Tests pour le training du modele sports."""
    
    def test_train_model_basic(self, small_sports_dataset, temp_models_dir):
        """Entrainement basique du modele sports."""
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
        
        df = small_sports_dataset
        
        # Preparer les donnees
        feature_cols = [
            'home_win_rate', 'away_win_rate',
            'home_goals_avg', 'away_goals_avg',
            'home_odds', 'draw_odds', 'away_odds'
        ]
        
        X = df[feature_cols]
        y = df['result']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Entrainer le modele
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)
        
        # Verifier les predictions
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Sur un dataset aleatoire, l'accuracy doit etre > 0.2
        assert accuracy > 0.2
        assert accuracy <= 1.0
    
    def test_save_and_load_model(self, small_sports_dataset, temp_models_dir):
        """Sauvegarde et chargement du modele."""
        from sklearn.model_selection import train_test_split
        
        df = small_sports_dataset
        
        feature_cols = [
            'home_win_rate', 'away_win_rate',
            'home_goals_avg', 'away_goals_avg',
            'home_odds', 'draw_odds', 'away_odds'
        ]
        
        X = df[feature_cols]
        y = df['result']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Entrainer
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)
        
        # Sauvegarder
        model_path = os.path.join(temp_models_dir, 'sports_model.pkl')
        joblib.dump(model, model_path)
        
        assert os.path.exists(model_path)
        
        # Recharger
        loaded_model = joblib.load(model_path)
        
        # Verifier que les predictions sont identiques
        pred_original = model.predict(X_test)
        pred_loaded = loaded_model.predict(X_test)
        
        assert all(pred_original == pred_loaded)
    
    def test_model_predict_proba(self, small_sports_dataset):
        """Le modele renvoie des probabilites."""
        from sklearn.model_selection import train_test_split
        
        df = small_sports_dataset
        
        feature_cols = [
            'home_win_rate', 'away_win_rate',
            'home_goals_avg', 'away_goals_avg',
            'home_odds', 'draw_odds', 'away_odds'
        ]
        
        X = df[feature_cols]
        y = df['result']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)
        
        # Obtenir les probabilites
        probas = model.predict_proba(X_test)
        
        # Verifier la forme
        assert probas.shape[0] == len(X_test)
        assert probas.shape[1] == 3  # home, draw, away
        
        # Verifier que chaque ligne somme a 1
        for row in probas:
            assert abs(row.sum() - 1.0) < 0.01
    
    def test_model_feature_importance(self, small_sports_dataset):
        """Le modele calcule l'importance des features."""
        from sklearn.model_selection import train_test_split
        
        df = small_sports_dataset
        
        feature_cols = [
            'home_win_rate', 'away_win_rate',
            'home_goals_avg', 'away_goals_avg',
            'home_odds', 'draw_odds', 'away_odds'
        ]
        
        X = df[feature_cols]
        y = df['result']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)
        
        # Verifier que les importances existent
        assert hasattr(model, 'feature_importances_')
        assert len(model.feature_importances_) == len(feature_cols)
        assert all(imp >= 0 for imp in model.feature_importances_)
