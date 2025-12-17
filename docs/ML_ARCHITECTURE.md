# 🧠 Machine Learning Architecture - PredictWise

## 📋 Vue d'ensemble

Architecture ML complète pour les prédictions sportives et financières avec feature engineering professionnel, entraînement supervisé et intégration backend.

---

## 🏗️ Architecture

```
ml/
├── features/               # Extraction de features
│   ├── sports_features.py    # 10 features sportives
│   └── finance_features.py   # 14 features financières
├── utils/                  # Utilitaires ML
│   ├── exceptions.py         # Exceptions custom
│   ├── validation.py         # Validation des données
│   └── preprocessing.py      # Préprocessing features
├── scripts/                # Scripts d'entraînement
│   ├── utils.py              # Helpers training
│   ├── train_sports_model.py # Entraîner modèle sports
│   └── train_finance_model.py# Entraîner modèle finance
├── models/                 # Modèles sauvegardés (.pkl)
│   ├── sports_model.pkl
│   ├── sports_scaler.pkl
│   ├── finance_model.pkl
│   └── finance_scaler.pkl
├── tests/                  # Tests unitaires
│   ├── test_sports_features.py
│   ├── test_finance_features.py
│   └── test_ml_service.py
└── data/                   # Données d'entraînement
    ├── raw/                  # Données brutes
    └── processed/            # Données processées
```

---

## 🎯 Modèles ML

### 1. **Modèle Sports (Match Predictions)**

**Type:** RandomForestClassifier

**Features (10):**
1. `form_diff` - Différence de forme récente (5 derniers matchs)
2. `attack_diff` - Différence de rating offensif
3. `defense_diff` - Différence de rating défensif
4. `goal_diff_ratio` - Ratio buts marqués/encaissés
5. `win_rate_diff` - Différence de taux de victoire
6. `home_advantage` - Avantage du terrain (0/1)
7. `xg_diff` - Différence xG (expected goals)
8. `h2h_home_rate` - Taux victoire historique domicile
9. `momentum_diff` - Différence de momentum
10. `fatigue_diff` - Différence de fatigue (repos)

**Classes de sortie:**
- `0` - Home Win (Victoire domicile)
- `1` - Draw (Match nul)
- `2` - Away Win (Victoire extérieur)

**Hyperparamètres:**
```python
RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42
)
```

### 2. **Modèle Finance (Asset Trend Predictions)**

**Type:** GradientBoostingClassifier

**Features (14):**
1. `change_1d` - % changement 1 jour
2. `change_5d` - % changement 5 jours
3. `change_10d` - % changement 10 jours
4. `ma7_diff` - % différence MA 7 jours
5. `ma20_diff` - % différence MA 20 jours
6. `ma50_diff` - % différence MA 50 jours
7. `volatility` - Volatilité 20 jours
8. `rsi_normalized` - RSI normalisé (-1 à 1)
9. `macd_diff` - Différence MACD
10. `momentum_5` - Momentum 5 jours
11. `momentum_10` - Momentum 10 jours
12. `volume_trend` - Tendance volume
13. `price_position` - Position prix (0-100)
14. `trend_strength` - Force tendance (-100 à 100)

**Classes de sortie:**
- `0` - UP (Hausse)
- `1` - NEUTRAL (Stable)
- `2` - DOWN (Baisse)

**Hyperparamètres:**
```python
GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    min_samples_split=10,
    random_state=42
)
```

---

## 🔄 Pipeline d'entraînement

### Étape 1: Génération de données synthétiques

```python
# Sports
python ml/scripts/train_sports_model.py
```

Génère 1000 matchs synthétiques avec distributions réalistes.

```python
# Finance
python ml/scripts/train_finance_model.py
```

Génère 1000 séries de prix avec tendances aléatoires.

### Étape 2: Extraction de features

```python
from ml.features.sports_features import SportsFeatureExtractor

extractor = SportsFeatureExtractor()
features = extractor.extract(match_data)  # (1, 10) array
```

### Étape 3: Normalisation

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

### Étape 4: Entraînement

```python
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
```

### Étape 5: Évaluation

- Accuracy
- Precision
- Recall
- F1-Score
- Confusion Matrix

### Étape 6: Sauvegarde

```python
import pickle

with open('ml/models/sports_model.pkl', 'wb') as f:
    pickle.dump(model, f)
```

---

## 🔌 Intégration Backend

### Service ML (`backend/app/services/ml_prediction_service.py`)

```python
from app.services.ml_prediction_service import get_prediction_service

service = get_prediction_service()

# Prédiction sports
result = service.predict_sport(match_data)
# {
#     "home_win_probability": 0.55,
#     "draw_probability": 0.25,
#     "away_win_probability": 0.20,
#     "confidence": 0.55,
#     "model_type": "RandomForestClassifier"
# }

# Prédiction finance
result = service.predict_finance(asset_data)
# {
#     "trend_prediction": "UP",
#     "up_probability": 0.60,
#     "neutral_probability": 0.25,
#     "down_probability": 0.15,
#     "confidence": 0.60,
#     "model_type": "GradientBoostingClassifier"
# }
```

### Fallback automatique

Si les modèles ne sont pas chargés ou erreur:
- Retourne prédictions par défaut (probabilités équilibrées)
- Confidence réduite (0.2-0.3)
- `model_type: "fallback"`

---

## 🧪 Tests unitaires

### Lancer tous les tests

```bash
# Depuis la racine du projet
cd ml
python -m pytest tests/ -v
```

### Tests individuels

```bash
# Features sports
python -m pytest tests/test_sports_features.py -v

# Features finance
python -m pytest tests/test_finance_features.py -v

# Service ML
python -m pytest tests/test_ml_service.py -v
```

### Couverture

```bash
pytest tests/ --cov=features --cov=utils --cov-report=html
```

---

## 📊 Exemple d'utilisation

### Sports Prediction

```python
# Données de match
match_data = {
    'home_form': [2, 1, 2, 1, 2],  # W, D, W, D, W
    'away_form': [0, 1, 0, 2, 1],  # L, D, L, W, D
    'home_attack': 78.5,
    'away_attack': 72.3,
    'home_defense': 81.2,
    'away_defense': 76.8,
    'home_goals_scored': 18,
    'away_goals_scored': 14,
    'home_goals_conceded': 9,
    'away_goals_conceded': 12,
    'home_win_rate': 0.68,
    'away_win_rate': 0.52,
    'is_home': True,
    'home_xg': [2.1, 1.8, 2.3, 1.6, 2.0],
    'away_xg': [1.4, 1.7, 1.2, 1.9, 1.5],
    'h2h_history': [1, 1, 0, 1, 2],  # Home wins, draws, away wins
    'home_rest_days': 4,
    'away_rest_days': 3
}

# Prédiction
from ml.features.sports_features import SportsFeatureExtractor

extractor = SportsFeatureExtractor()
features = extractor.extract(match_data)

print(features.shape)  # (1, 10)
print(features)
# [[1.5, 6.2, 4.4, 0.82, 0.16, 1.0, 0.6, 0.75, 0.8, 1.0]]
```

### Finance Prediction

```python
# Données d'asset
asset_data = {
    'price_history': [
        100.0, 101.2, 102.5, 101.8, 103.2,  # 5 jours
        104.1, 103.8, 105.2, 106.0, 105.5,  # 10 jours
        # ... 50+ points requis
    ],
    'volume_history': [
        5000, 5200, 4800, 5100, 5300,
        # ... correspond à price_history
    ]
}

# Prédiction
from ml.features.finance_features import FinanceFeatureExtractor

extractor = FinanceFeatureExtractor()
features = extractor.extract(asset_data)

print(features.shape)  # (1, 14)
print(features)
# [[1.2, 3.2, 5.5, 0.8, 1.2, 2.1, 2.3, 0.15, 0.05, 3.1, 5.2, 0.2, 68.5, 45.2]]
```

---

## 🔧 Configuration

### Requirements

```txt
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
pytest>=7.4.0
```

Installation:

```bash
cd ml
pip install -r requirements.txt
```

---

## ⚠️ Disclaimers

### **IMPORTANT - Projet éducatif uniquement**

1. **Pas de trading réel**: Ces modèles sont pour l'apprentissage uniquement
2. **Données synthétiques**: Entraînés sur données générées, pas réelles
3. **Pas de conseil financier**: Ne jamais utiliser pour investissements réels
4. **Pas de paris sportifs**: Ne jamais utiliser pour paris d'argent réel

### Limitations

- Modèles basiques (RandomForest, GradientBoosting)
- Features simplifiées (pas de NLP, pas de données externes)
- Données synthétiques (pas de données historiques réelles)
- Pas de backtesting sur données réelles
- Pas d'optimisation hyperparamètres avancée
- Pas de modèles deep learning

---

## 🚀 Améliorations futures

### Phase 1: Données réelles
- [ ] Scraper données historiques sports (API-Football)
- [ ] Intégrer données financières réelles (Yahoo Finance, Alpha Vantage)
- [ ] Créer datasets labeled manuellement

### Phase 2: Features avancées
- [ ] Features NLP (news sentiment, tweets)
- [ ] Features contextuelles (météo, blessures, etc.)
- [ ] Features temporelles (jour semaine, période saison)
- [ ] Feature engineering automatique (AutoML)

### Phase 3: Modèles avancés
- [ ] XGBoost, LightGBM
- [ ] Réseaux neuronaux (LSTM pour séries temporelles)
- [ ] Ensembles de modèles (stacking, blending)
- [ ] AutoML (TPOT, Auto-sklearn)

### Phase 4: Validation robuste
- [ ] Cross-validation temporelle
- [ ] Backtesting sur données réelles
- [ ] Métriques métier (ROI, Sharpe ratio pour finance)
- [ ] A/B testing prédictions

### Phase 5: Production
- [ ] API prédictions en temps réel
- [ ] Monitoring performance modèles
- [ ] Re-entraînement automatique
- [ ] Déploiement cloud (AWS SageMaker, GCP AI Platform)

---

## 📚 Ressources

### Documentation
- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Feature Engineering for ML](https://www.oreilly.com/library/view/feature-engineering-for/9781491953235/)
- [Hands-On ML with Scikit-Learn](https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/)

### Datasets publics
- [API-Football](https://www.api-football.com/) - Données sports
- [Yahoo Finance API](https://pypi.org/project/yfinance/) - Données financières
- [Kaggle Sports Datasets](https://www.kaggle.com/datasets?search=sports)

---

## 🤝 Contribution

Pour ajouter de nouvelles features:

1. Créer nouvelle classe dans `ml/features/`
2. Hériter de `BaseFeatureExtractor`
3. Implémenter `extract()` et `REQUIRED_FEATURES`
4. Ajouter tests dans `ml/tests/`
5. Mettre à jour documentation

---

## 📝 License

**Educational Use Only** - Ne pas utiliser pour applications commerciales ou financières réelles.

---

**Créé avec ❤️ pour l'apprentissage du Machine Learning**
