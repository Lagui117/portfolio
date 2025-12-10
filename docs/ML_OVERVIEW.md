# ML Overview - PredictWise

## Vue d'ensemble

PredictWise utilise des modèles de Machine Learning pour prédire :
- **Sports** : Résultats de matchs (Victoire à domicile, Match nul, Victoire à l'extérieur)
- **Finance** : Tendances boursières (Hausse, Baisse)

## Architecture ML

```
ml/
├── data/               # Datasets bruts (CSV, non versionnés)
├── models/            # Modèles entraînés (.pkl)
│   ├── sports_model.pkl
│   ├── finance_model.pkl
│   └── finance_scaler.pkl
├── notebooks/         # Jupyter notebooks d'exploration
│   ├── sports_exploration.ipynb
│   ├── finance_exploration.ipynb
│   └── feature_engineering.ipynb
└── scripts/           # Scripts d'entraînement et évaluation
    ├── train_sports_model.py
    ├── train_finance_model.py
    └── evaluate_models.py
```

---

## 1. Sports Prediction Model

### Algorithme
**RandomForestClassifier** (scikit-learn)
- **Paramètres** :
  - `n_estimators=200` : 200 arbres de décision
  - `max_depth=15` : Profondeur maximale de 15 niveaux
  - `min_samples_split=10` : Minimum 10 échantillons pour une division
  - `min_samples_leaf=5` : Minimum 5 échantillons par feuille
  - `random_state=42` : Reproductibilité

### Features (13 caractéristiques)

#### Statistiques des équipes
1. **home_win_rate** : Taux de victoires de l'équipe à domicile
2. **home_avg_goals_scored** : Moyenne de buts marqués par l'équipe à domicile
3. **home_recent_form** : Forme récente de l'équipe à domicile (points/match sur 5 derniers)
4. **away_win_rate** : Taux de victoires de l'équipe visiteuse
5. **away_avg_goals_scored** : Moyenne de buts marqués par l'équipe visiteuse
6. **away_recent_form** : Forme récente de l'équipe visiteuse

#### Features dérivées
7. **win_rate_diff** : Différence de taux de victoires (home - away)
8. **form_diff** : Différence de forme (home - away)
9. **h2h_home_win_rate** : Taux de victoires à domicile en confrontations directes

#### Cotes de paris
10. **home_odds** : Cote pour victoire à domicile
11. **draw_odds** : Cote pour match nul
12. **away_odds** : Cote pour victoire à l'extérieur
13. **odds_ratio** : Ratio home_odds / away_odds

### Classes cibles
- `HOME_WIN` : Victoire de l'équipe à domicile
- `DRAW` : Match nul
- `AWAY_WIN` : Victoire de l'équipe visiteuse

### Performance

Sur un dataset de test de 1000 matchs :

| Métrique | Valeur |
|----------|--------|
| **Accuracy** | ~41% |
| **Precision (weighted)** | ~0.40 |
| **Recall (weighted)** | ~0.41 |
| **F1-Score (weighted)** | ~0.40 |

#### Performance par classe
| Classe | Precision | Recall | F1-Score |
|--------|-----------|--------|----------|
| HOME_WIN | ~0.42 | ~0.48 | ~0.45 |
| DRAW | ~0.35 | ~0.25 | ~0.29 |
| AWAY_WIN | ~0.40 | ~0.43 | ~0.41 |

### Entraînement

```bash
cd ml/scripts
python train_sports_model.py
```

**Données d'entraînement** : 5000 matchs synthétiques avec distribution réaliste
**Validation** : 5-fold cross-validation
**Sortie** : `ml/models/sports_model.pkl` (environ 13 MB)

### Features les plus importantes
1. **home_odds** : Cote de victoire à domicile
2. **away_odds** : Cote de victoire à l'extérieur
3. **win_rate_diff** : Différence de taux de victoires
4. **odds_ratio** : Ratio des cotes
5. **home_win_rate** : Taux de victoires à domicile

---

## 2. Finance Prediction Model

### Algorithme
**LogisticRegression** (scikit-learn)
- **Paramètres** :
  - `max_iter=1000` : Maximum 1000 itérations
  - `random_state=42` : Reproductibilité
  - `solver='lbfgs'` : Optimiseur L-BFGS
- **Preprocessing** : StandardScaler pour normalisation des features

### Features (14 caractéristiques)

#### Moyennes mobiles (Moving Averages)
1. **MA_5** : Moyenne mobile 5 jours
2. **MA_20** : Moyenne mobile 20 jours
3. **MA_50** : Moyenne mobile 50 jours

#### Indicateurs techniques
4. **RSI** : Relative Strength Index (14 périodes)
5. **MACD** : Moving Average Convergence Divergence

#### Volatilité
6. **volatility_daily** : Volatilité journalière
7. **volatility_annual** : Volatilité annualisée (√252)

#### Changements de prix
8. **price_change_1d** : Variation sur 1 jour (%)
9. **price_change_5d** : Variation sur 5 jours (%)
10. **price_change_20d** : Variation sur 20 jours (%)

#### Features dérivées
11. **ma5_minus_ma20** : Différence MA5 - MA20
12. **ma20_minus_ma50** : Différence MA20 - MA50
13. **ma5_ratio** : Ratio MA5 / prix actuel
14. **ma20_ratio** : Ratio MA20 / prix actuel

### Classes cibles
- `UP` : Tendance haussière (prix en hausse)
- `DOWN` : Tendance baissière (prix en baisse)

### Performance

Sur un dataset de test de 600 actions :

| Métrique | Valeur |
|----------|--------|
| **Accuracy** | ~56% |
| **Precision** | ~0.56 |
| **Recall** | ~0.58 |
| **F1-Score** | ~0.57 |
| **ROC AUC** | ~0.56 |

### Entraînement

```bash
cd ml/scripts
python train_finance_model.py
```

**Données d'entraînement** : 3000 séries temporelles synthétiques
**Validation** : 5-fold cross-validation
**Sorties** :
- `ml/models/finance_model.pkl` (environ 1.2 KB)
- `ml/models/finance_scaler.pkl` (environ 1.4 KB)

### Features les plus importantes
1. **price_change_5d** : Variation sur 5 jours (momentum court terme)
2. **MA_5** : Moyenne mobile courte période
3. **MACD** : Convergence/divergence des moyennes mobiles
4. **RSI** : Index de force relative
5. **ma5_minus_ma20** : Croisement des moyennes mobiles

---

## 3. Évaluation des modèles

### Script d'évaluation

```bash
cd ml/scripts
python evaluate_models.py
```

Ce script :
- Charge les modèles entraînés
- Génère des datasets de test (distributions réalistes)
- Calcule les métriques détaillées :
  - Accuracy, Precision, Recall, F1-Score
  - Matrice de confusion
  - Rapport de classification complet
  - Importance des features
- Affiche des exemples de prédictions

### Métriques disponibles

**Sports Model** :
- Accuracy par classe (HOME_WIN, DRAW, AWAY_WIN)
- Matrice de confusion 3x3
- Importance des features (feature importance)

**Finance Model** :
- Accuracy binaire (UP vs DOWN)
- ROC AUC Score
- Coefficients du modèle logistique

---

## 4. Service de prédiction

### Architecture

Le service `prediction_service.py` centralise toutes les prédictions ML :

```python
from backend.app.services.prediction_service import get_prediction_service

service = get_prediction_service()

# Sports prediction
result = service.predict_sport_event(
    home_stats={'win_rate': 0.6, 'avg_goals_scored': 2.1, 'recent_form': 2.5},
    away_stats={'win_rate': 0.45, 'avg_goals_scored': 1.6, 'recent_form': 1.8},
    odds={'home': 1.8, 'draw': 3.5, 'away': 4.2}
)

# Finance prediction
result = service.predict_stock_movement(
    technical_indicators={
        'MA_5': 152.3, 'MA_20': 148.7, 'MA_50': 145.2,
        'RSI': 62.5, 'MACD': 2.1,
        'volatility_daily': 0.025, 'volatility_annual': 0.40,
        'price_change_1d': 0.012, 'price_change_5d': 0.035,
        'price_change_20d': 0.068, 'current_price': 153.5
    }
)
```

### Fallback Strategy

Si les modèles ne sont pas disponibles, le service utilise des prédictions basées sur des règles :
- **Sports** : Calcul de force relative basé sur win_rate et form
- **Finance** : Règles basées sur RSI, MACD, MA crossovers

---

## 5. Utilisation dans le backend

### Endpoints API

#### Sports
```
POST /api/sports/predict
Body: {
  "home_team_id": 1,
  "away_team_id": 2,
  "match_date": "2024-01-15"
}
```

#### Finance
```
POST /api/finance/predict
Body: {
  "symbol": "AAPL",
  "days_ahead": 5
}
```

### Intégration

Les services `sports_service.py` et `finance_service.py` utilisent le `prediction_service` :

```python
from backend.app.services.prediction_service import get_prediction_service

service = get_prediction_service()
prediction = service.predict_sport_event(home_stats, away_stats, odds)
```

---

## 6. Datasets et Features Engineering

### Génération de données synthétiques

Les scripts de training génèrent des données synthétiques réalistes :

**Sports** :
- Distribution des taux de victoires (0.2 - 0.8)
- Forme récente (0 - 3 points/match)
- Cotes de paris corrélées aux forces des équipes
- Résultats basés sur probabilités réalistes

**Finance** :
- Séries temporelles avec drift et volatilité
- Indicateurs techniques calculés (MA, RSI, MACD)
- Tendances haussières/baissières équilibrées

### Features Engineering

**Normalisation** :
- Sports : Pas de normalisation (Random Forest robuste)
- Finance : StandardScaler (important pour régression logistique)

**Features dérivées** :
- Différences (win_rate_diff, form_diff)
- Ratios (odds_ratio, ma5_ratio)
- Croisements (ma5_minus_ma20)

---

## 7. Améliorations futures

### Données réelles
- Intégration API sports (Sportradar, The Odds API)
- Intégration API finance (Alpha Vantage, Yahoo Finance)
- Stockage des prédictions et résultats réels
- Réentraînement périodique avec données actualisées

### Modèles avancés
- **Sports** : XGBoost, Neural Networks, Ensemble methods
- **Finance** : LSTM pour séries temporelles, Prophet
- Hyperparameter tuning avec GridSearchCV

### Features supplémentaires
- **Sports** : Blessures, météo, statistiques joueurs
- **Finance** : Volume, sentiment analysis, actualités

### Monitoring
- Drift detection (changements de distribution)
- Performance tracking en production
- A/B testing de nouveaux modèles

---

## 8. Disclaimer

⚠️ **AVERTISSEMENT IMPORTANT**

Ces modèles de Machine Learning sont destinés à des **fins éducatives et de démonstration uniquement**.

**NE PAS UTILISER** pour :
- Paris sportifs réels avec de l'argent
- Décisions d'investissement financier
- Conseils professionnels

**Limites** :
- Données synthétiques (non réelles)
- Performance modeste (~41% sports, ~56% finance)
- Pas de garantie de performance future
- Simplification de problèmes complexes

**Prédire l'avenir est intrinsèquement incertain.**

---

## 9. Commandes rapides

```bash
# Entraîner tous les modèles
cd ml/scripts
python train_sports_model.py
python train_finance_model.py

# Évaluer les modèles
python evaluate_models.py

# Vérifier les modèles chargés
cd backend
python -c "from app.services.prediction_service import get_prediction_service; print(get_prediction_service().get_models_info())"
```

---

## 10. Références

### Bibliothèques utilisées
- **scikit-learn 1.3.2** : https://scikit-learn.org/
- **pandas 2.1.4** : https://pandas.pydata.org/
- **numpy 1.26.2** : https://numpy.org/
- **joblib** : https://joblib.readthedocs.io/

### Algorithmes
- **Random Forest** : https://scikit-learn.org/stable/modules/ensemble.html#forest
- **Logistic Regression** : https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression

### Indicateurs techniques
- **RSI** : Relative Strength Index (Wilder)
- **MACD** : Moving Average Convergence Divergence (Appel)
- **Moving Averages** : Simple Moving Average (SMA)

---

*Documentation générée pour PredictWise - Version 1.0*
