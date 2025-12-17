# 🚀 Guide de démarrage rapide - ML Pipeline

## Installation

```bash
# 1. Installer dépendances ML
cd ml
pip install -r requirements.txt

# 2. Créer dossiers nécessaires
mkdir -p models data/raw data/processed
```

## Entraîner les modèles

### Sports Model

```bash
python scripts/train_sports_model.py
```

**Sortie attendue:**
```
================================================================================
  SPORTS PREDICTION MODEL TRAINING
================================================================================
Dataset: 1000 samples
Features: 10
Classes: 3 (Home Win, Draw, Away Win)

Training model...
✓ Model trained successfully

Evaluating model...
Accuracy: 0.85
Precision: 0.84
Recall: 0.85
F1-Score: 0.84

Confusion Matrix saved to ml/models/sports_confusion_matrix.png
Model saved to ml/models/sports_model.pkl
Scaler saved to ml/models/sports_scaler.pkl
```

### Finance Model

```bash
python scripts/train_finance_model.py
```

**Sortie attendue:**
```
================================================================================
  FINANCE PREDICTION MODEL TRAINING
================================================================================
Dataset: 1000 samples
Features: 14
Classes: 3 (UP, NEUTRAL, DOWN)

Training model...
✓ Model trained successfully

Evaluating model...
Accuracy: 0.82
Precision: 0.81
Recall: 0.82
F1-Score: 0.81

Confusion Matrix saved to ml/models/finance_confusion_matrix.png
Model saved to ml/models/finance_model.pkl
Scaler saved to ml/models/finance_scaler.pkl
```

## Tester les modèles

```bash
# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_sports_features.py -v
pytest tests/test_finance_features.py -v
pytest tests/test_ml_service.py -v
```

## Utilisation dans le backend

### 1. Intégrer le service ML

Dans `backend/app/services/prediction_service.py`:

```python
from app.services.ml_prediction_service import get_prediction_service

ml_service = get_prediction_service()

def predict_match_outcome(match_data):
    """Utiliser ML pour prédire résultat match."""
    result = ml_service.predict_sport(match_data)
    return result

def predict_asset_trend(asset_data):
    """Utiliser ML pour prédire tendance asset."""
    result = ml_service.predict_finance(asset_data)
    return result
```

### 2. API Endpoint exemple

Dans `backend/app/api/v1/ai.py`:

```python
from app.services.ml_prediction_service import get_prediction_service

@router.post("/predict/sports")
async def predict_sports_match(match_data: dict):
    """
    Prédire résultat match sportif.
    
    Body:
    {
        "home_form": [2, 1, 2, 1, 2],
        "away_form": [1, 0, 1, 2, 0],
        "home_attack": 75.5,
        "away_attack": 68.2,
        ...
    }
    """
    ml_service = get_prediction_service()
    prediction = ml_service.predict_sport(match_data)
    
    return {
        "success": True,
        "prediction": prediction
    }

@router.post("/predict/finance")
async def predict_finance_trend(asset_data: dict):
    """
    Prédire tendance asset financier.
    
    Body:
    {
        "price_history": [100, 101, 102, ...],
        "volume_history": [5000, 5100, 4900, ...]
    }
    """
    ml_service = get_prediction_service()
    prediction = ml_service.predict_finance(asset_data)
    
    return {
        "success": True,
        "prediction": prediction
    }
```

## Exemple Frontend

```javascript
// services/mlService.js
import apiClient from './apiClient';

export const predictSportsMatch = async (matchData) => {
  const response = await apiClient.post('/api/v1/ai/predict/sports', matchData);
  return response.data;
};

export const predictFinanceTrend = async (assetData) => {
  const response = await apiClient.post('/api/v1/ai/predict/finance', assetData);
  return response.data;
};

// Utilisation dans composant
const handlePredict = async () => {
  const matchData = {
    home_form: [2, 1, 2, 1, 2],
    away_form: [1, 0, 1, 2, 0],
    home_attack: 75.5,
    away_attack: 68.2,
    // ...
  };
  
  const result = await predictSportsMatch(matchData);
  
  console.log(result.prediction);
  // {
  //   home_win_probability: 0.55,
  //   draw_probability: 0.25,
  //   away_win_probability: 0.20,
  //   confidence: 0.55
  // }
};
```

## Vérifier status modèles

```python
from app.services.ml_prediction_service import get_prediction_service

service = get_prediction_service()
info = service.get_model_info()

print(info)
# {
#   "sports_model_loaded": True,
#   "sports_model_type": "RandomForestClassifier",
#   "finance_model_loaded": True,
#   "finance_model_type": "GradientBoostingClassifier",
#   "models_directory": "/path/to/ml/models"
# }
```

## Debugging

### Problème: Modèles non chargés

```bash
# Vérifier fichiers
ls -la ml/models/
# Devrait montrer:
# sports_model.pkl
# sports_scaler.pkl
# finance_model.pkl
# finance_scaler.pkl

# Re-entraîner si manquant
python ml/scripts/train_sports_model.py
python ml/scripts/train_finance_model.py
```

### Problème: Erreur import

```bash
# Vérifier structure
ls -la ml/features/
ls -la ml/utils/

# Vérifier __init__.py
cat ml/features/__init__.py
cat ml/utils/__init__.py
```

### Problème: Prédictions fallback

Le service retourne automatiquement des prédictions par défaut si:
- Modèles non entraînés
- Données invalides
- Erreur pendant prédiction

**Solution**: Vérifier logs et re-entraîner modèles.

## Performance attendue

### Sports Model
- **Accuracy**: ~85%
- **Temps prédiction**: <50ms
- **Features**: 10
- **Classes**: 3 (Home/Draw/Away)

### Finance Model
- **Accuracy**: ~82%
- **Temps prédiction**: <100ms
- **Features**: 14
- **Classes**: 3 (UP/NEUTRAL/DOWN)

## Next Steps

1. ✅ Entraîner modèles
2. ✅ Tester extraction features
3. ✅ Intégrer dans backend
4. ✅ Créer endpoints API
5. ✅ Tester depuis frontend
6. 🔄 Collecter données réelles
7. 🔄 Re-entraîner avec vraies données
8. 🔄 Optimiser hyperparamètres

---

**Note**: Ces modèles sont entraînés sur données synthétiques pour démonstration. Pour production, utiliser données réelles et validation rigoureuse.
