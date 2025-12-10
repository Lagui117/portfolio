# Machine Learning - PredictWise

Ce dossier contient tous les éléments relatifs au Machine Learning du projet PredictWise.

## 📁 Structure

```
ml/
├── data/               # Datasets bruts (CSV, non versionnés)
├── models/            # Modèles entraînés (.pkl)
│   ├── sports_model.pkl         # RandomForest pour prédictions sportives
│   ├── finance_model.pkl        # LogisticRegression pour finance
│   └── finance_scaler.pkl       # StandardScaler pour normalisation
├── notebooks/         # Jupyter notebooks d'exploration (optionnel)
├── scripts/           # Scripts Python pour ML
│   ├── train_sports_model.py    # Entraînement modèle sports
│   ├── train_finance_model.py   # Entraînement modèle finance
│   └── evaluate_models.py       # Évaluation des modèles
└── README.md          # Ce fichier
```

## 🚀 Démarrage rapide

### 1. Entraîner les modèles

```bash
cd ml/scripts

# Entraîner le modèle sports (5000 matchs synthétiques)
python train_sports_model.py

# Entraîner le modèle finance (3000 séries temporelles)
python train_finance_model.py
```

**Sortie** : Les modèles `.pkl` sont sauvegardés dans `ml/models/`

### 2. Évaluer les modèles

```bash
cd ml/scripts
python evaluate_models.py
```

**Affiche** :
- Métriques détaillées (accuracy, precision, recall, F1-score)
- Matrices de confusion
- Classification reports
- Exemples de prédictions

### 3. Utiliser les modèles dans le backend

Les modèles sont automatiquement chargés par le backend Flask via `prediction_service.py`.

```python
from backend.app.services.prediction_service import get_prediction_service

service = get_prediction_service()

# Prédiction sportive
result = service.predict_sport_event(
    home_stats={'win_rate': 0.65, 'avg_goals_scored': 2.2, 'recent_form': 2.5},
    away_stats={'win_rate': 0.48, 'avg_goals_scored': 1.7, 'recent_form': 1.9}
)

# Prédiction financière
result = service.predict_stock_movement(
    technical_indicators={
        'MA_5': 150.2, 'MA_20': 147.8, 'RSI': 58.3, 
        'MACD': 1.5, 'current_price': 151.0, ...
    }
)
```

## 🏆 Modèles

### Sports Prediction Model

| Propriété | Valeur |
|-----------|--------|
| **Algorithme** | RandomForestClassifier |
| **Features** | 13 (win_rate, form, odds, etc.) |
| **Classes** | HOME_WIN, DRAW, AWAY_WIN |
| **Accuracy** | ~41% |
| **Taille** | ~13 MB |

**Features principales** :
- Statistiques des équipes (win_rate, avg_goals, form)
- Cotes de paris (home_odds, draw_odds, away_odds)
- Features dérivées (win_rate_diff, form_diff, odds_ratio)

### Finance Prediction Model

| Propriété | Valeur |
|-----------|--------|
| **Algorithme** | LogisticRegression + StandardScaler |
| **Features** | 14 (MA, RSI, MACD, volatility, etc.) |
| **Classes** | UP, DOWN |
| **Accuracy** | ~56% |
| **Taille** | ~2.6 KB (model + scaler) |

**Indicateurs techniques** :
- Moyennes mobiles (MA_5, MA_20, MA_50)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Volatilité, changements de prix

## 📊 Évaluation

### Métriques calculées

**Sports** :
```
Accuracy:  0.41 (41%)
Precision: 0.40 (weighted)
Recall:    0.41 (weighted)
F1-Score:  0.40 (weighted)
```

**Finance** :
```
Accuracy:  0.56 (56%)
Precision: 0.56
Recall:    0.58
F1-Score:  0.57
ROC AUC:   0.56
```

### Exécuter l'évaluation

```bash
cd ml/scripts
python evaluate_models.py
```

Le script affiche :
- ✅ Métriques globales et par classe
- 📋 Matrices de confusion
- 📈 Rapports de classification détaillés
- 🔍 Importance des features
- 🎯 Exemples de prédictions

## 🛠️ Développement

### Prérequis

Les dépendances ML sont déjà installées (voir `backend/requirements.txt`) :
```
scikit-learn==1.3.2
pandas==2.1.4
numpy==1.26.2
joblib
```

### Ajouter de nouvelles features

1. **Modifier le script d'entraînement** (`train_*_model.py`)
2. **Ajouter les features dans la fonction de génération de données**
3. **Mettre à jour `prediction_service.py`** pour préparer les features
4. **Réentraîner le modèle**
5. **Évaluer les performances**

### Tester un nouveau modèle

```python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

# Exemple : tester GradientBoosting pour sports
model = GradientBoostingClassifier(n_estimators=100)
scores = cross_val_score(model, X, y, cv=5)
print(f"Accuracy: {scores.mean():.4f} (+/- {scores.std():.4f})")
```

## 📝 Notebooks (optionnel)

Le dossier `notebooks/` peut contenir des Jupyter notebooks pour :
- **Exploration de données** : Visualiser distributions, corrélations
- **Feature engineering** : Tester nouvelles features
- **Prototypage de modèles** : Expérimenter différents algorithmes

Exemples suggérés :
- `sports_exploration.ipynb` : Analyse des features sportives
- `finance_exploration.ipynb` : Analyse des indicateurs techniques
- `feature_engineering.ipynb` : Création et test de nouvelles features

## 🔄 Workflow ML

```
1. Génération de données synthétiques
   ↓
2. Feature engineering
   ↓
3. Entraînement du modèle
   ↓
4. Validation croisée (5-fold CV)
   ↓
5. Sauvegarde du modèle (.pkl)
   ↓
6. Évaluation sur données de test
   ↓
7. Intégration dans le backend
   ↓
8. Utilisation via API REST
```

## ⚠️ Disclaimer

**Ces modèles sont à des fins éducatives uniquement.**

- ❌ Ne PAS utiliser pour paris sportifs réels
- ❌ Ne PAS utiliser pour investissements financiers
- ⚠️ Données synthétiques (non réelles)
- ⚠️ Performance modeste
- ⚠️ Pas de garantie de performance future

## 📚 Documentation complète

Pour plus de détails, consultez :
- **[ML_OVERVIEW.md](../docs/ML_OVERVIEW.md)** : Documentation complète du ML
- **[API_SPEC.md](../docs/API_SPEC.md)** : Spécification des endpoints API
- **[README.md](../README.md)** : Documentation générale du projet

## 🧪 Tests

```bash
# Vérifier que les modèles peuvent être chargés
cd backend
python -c "from app.services.prediction_service import get_prediction_service; print(get_prediction_service().get_models_info())"

# Exemple de sortie :
# {
#   'sports_model': {'loaded': True, 'type': 'RandomForestClassifier', ...},
#   'finance_model': {'loaded': True, 'type': 'LogisticRegression', ...}
# }
```

## 💡 Conseils

1. **Réentraîner régulièrement** : Si vous modifiez les features
2. **Comparer les versions** : Gardez trace des performances de chaque version
3. **Valider sur données de test** : Toujours évaluer sur données non vues
4. **Monitorer en production** : Suivre l'accuracy réelle des prédictions

## 🔗 Liens utiles

- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Random Forest Guide](https://scikit-learn.org/stable/modules/ensemble.html#forest)
- [Logistic Regression Guide](https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression)
- [Feature Engineering Best Practices](https://scikit-learn.org/stable/modules/preprocessing.html)

---

*Machine Learning pour PredictWise - Version 1.0*
