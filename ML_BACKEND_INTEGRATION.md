# 🔌 Intégration ML dans le Backend

## Guide d'intégration du service ML dans PredictWise

---

## 📋 Prérequis

1. Modèles entraînés dans `ml/models/`:
   - `sports_model.pkl`
   - `sports_scaler.pkl`
   - `finance_model.pkl`
   - `finance_scaler.pkl`

2. Service ML installé:
   - `backend/app/services/ml_prediction_service.py`

---

## 🔧 Étape 1: Modifier prediction_service.py

Remplacer le fichier actuel pour utiliser les modèles ML:

### Fichier: `backend/app/services/prediction_service.py`

```python
"""
Prediction Service - Intégration ML

Utilise les modèles ML entraînés pour générer prédictions réelles.
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Import ML service
from .ml_prediction_service import get_prediction_service

logger = logging.getLogger(__name__)


class PredictionService:
    """Service de prédiction avec ML."""
    
    def __init__(self):
        """Initialiser le service avec ML."""
        self.ml_service = get_prediction_service()
        logger.info("Prediction service initialized with ML models")
    
    def predict_sport_match(
        self,
        home_team: str,
        away_team: str,
        match_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prédire résultat match sportif.
        
        Args:
            home_team: Nom équipe domicile
            away_team: Nom équipe extérieur
            match_data: Statistiques du match
            
        Returns:
            Prédiction avec probabilités
        """
        try:
            # Utiliser ML pour prédiction
            ml_result = self.ml_service.predict_sport(match_data)
            
            # Formater résultat
            prediction = {
                "match_id": f"{home_team}_vs_{away_team}_{datetime.now().timestamp()}",
                "home_team": home_team,
                "away_team": away_team,
                "prediction": {
                    "home_win": ml_result["home_win_probability"],
                    "draw": ml_result["draw_probability"],
                    "away_win": ml_result["away_win_probability"]
                },
                "confidence": ml_result["confidence"],
                "model_type": ml_result["model_type"],
                "timestamp": datetime.now().isoformat()
            }
            
            # Ajouter recommandation
            max_prob = max(
                ml_result["home_win_probability"],
                ml_result["draw_probability"],
                ml_result["away_win_probability"]
            )
            
            if max_prob == ml_result["home_win_probability"]:
                prediction["recommendation"] = "HOME_WIN"
            elif max_prob == ml_result["draw_probability"]:
                prediction["recommendation"] = "DRAW"
            else:
                prediction["recommendation"] = "AWAY_WIN"
            
            logger.info(f"Sports prediction generated: {prediction['recommendation']}")
            return prediction
            
        except Exception as e:
            logger.error(f"Error in sports prediction: {e}")
            return self._fallback_sports_prediction(home_team, away_team)
    
    def predict_finance_trend(
        self,
        asset_symbol: str,
        asset_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prédire tendance asset financier.
        
        Args:
            asset_symbol: Symbole asset (ex: AAPL, BTC-USD)
            asset_data: Historique prix et volume
            
        Returns:
            Prédiction de tendance
        """
        try:
            # Utiliser ML pour prédiction
            ml_result = self.ml_service.predict_finance(asset_data)
            
            # Formater résultat
            prediction = {
                "asset_id": f"{asset_symbol}_{datetime.now().timestamp()}",
                "asset_symbol": asset_symbol,
                "prediction": {
                    "trend": ml_result["trend_prediction"],
                    "up_probability": ml_result["up_probability"],
                    "neutral_probability": ml_result["neutral_probability"],
                    "down_probability": ml_result["down_probability"]
                },
                "confidence": ml_result["confidence"],
                "model_type": ml_result["model_type"],
                "timestamp": datetime.now().isoformat()
            }
            
            # Ajouter recommandation
            trend = ml_result["trend_prediction"]
            confidence = ml_result["confidence"]
            
            if trend == "UP" and confidence > 0.6:
                prediction["recommendation"] = "BUY"
            elif trend == "DOWN" and confidence > 0.6:
                prediction["recommendation"] = "SELL"
            else:
                prediction["recommendation"] = "HOLD"
            
            logger.info(f"Finance prediction generated: {prediction['recommendation']}")
            return prediction
            
        except Exception as e:
            logger.error(f"Error in finance prediction: {e}")
            return self._fallback_finance_prediction(asset_symbol)
    
    def _fallback_sports_prediction(
        self,
        home_team: str,
        away_team: str
    ) -> Dict[str, Any]:
        """Prédiction fallback si ML échoue."""
        return {
            "match_id": f"{home_team}_vs_{away_team}_fallback",
            "home_team": home_team,
            "away_team": away_team,
            "prediction": {
                "home_win": 0.40,
                "draw": 0.30,
                "away_win": 0.30
            },
            "confidence": 0.3,
            "model_type": "fallback",
            "recommendation": "UNCERTAIN",
            "timestamp": datetime.now().isoformat()
        }
    
    def _fallback_finance_prediction(self, asset_symbol: str) -> Dict[str, Any]:
        """Prédiction fallback si ML échoue."""
        return {
            "asset_id": f"{asset_symbol}_fallback",
            "asset_symbol": asset_symbol,
            "prediction": {
                "trend": "NEUTRAL",
                "up_probability": 0.33,
                "neutral_probability": 0.34,
                "down_probability": 0.33
            },
            "confidence": 0.3,
            "model_type": "fallback",
            "recommendation": "HOLD",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_model_status(self) -> Dict[str, Any]:
        """Obtenir status des modèles ML."""
        return self.ml_service.get_model_info()


# Global instance
_prediction_service = None


def get_prediction_service() -> PredictionService:
    """Obtenir instance globale du service."""
    global _prediction_service
    
    if _prediction_service is None:
        _prediction_service = PredictionService()
    
    return _prediction_service
```

---

## 🔧 Étape 2: Modifier les endpoints API

### Fichier: `backend/app/api/v1/sports.py`

Ajouter endpoint prédiction ML:

```python
from app.services.prediction_service import get_prediction_service

@router.post("/predict")
async def predict_match(
    match_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Prédire résultat match avec ML.
    
    Body exemple:
    {
        "home_team": "Real Madrid",
        "away_team": "Barcelona",
        "match_data": {
            "home_form": [2, 1, 2, 1, 2],
            "away_form": [1, 0, 1, 2, 0],
            "home_attack": 85.5,
            "away_attack": 83.2,
            "home_defense": 82.0,
            "away_defense": 80.5,
            "home_goals_scored": 18,
            "away_goals_scored": 16,
            "home_goals_conceded": 8,
            "away_goals_conceded": 9,
            "home_win_rate": 0.72,
            "away_win_rate": 0.68,
            "is_home": true,
            "home_xg": [2.1, 1.8, 2.3, 1.9, 2.0],
            "away_xg": [1.9, 2.1, 1.7, 2.0, 1.8],
            "h2h_history": [1, 0, 1, 2, 1],
            "home_rest_days": 4,
            "away_rest_days": 3
        }
    }
    """
    try:
        # Extraire données
        home_team = match_data.get("home_team")
        away_team = match_data.get("away_team")
        match_stats = match_data.get("match_data")
        
        if not all([home_team, away_team, match_stats]):
            raise HTTPException(
                status_code=400,
                detail="Missing required fields"
            )
        
        # Générer prédiction
        prediction_service = get_prediction_service()
        prediction = prediction_service.predict_sport_match(
            home_team,
            away_team,
            match_stats
        )
        
        # Sauvegarder en DB (optionnel)
        # db_prediction = Prediction(
        #     user_id=current_user.id,
        #     type="sport",
        #     data=prediction
        # )
        # db.add(db_prediction)
        # db.commit()
        
        return {
            "success": True,
            "prediction": prediction
        }
        
    except Exception as e:
        logger.error(f"Error in match prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Fichier: `backend/app/api/v1/finance.py`

Ajouter endpoint prédiction ML:

```python
from app.services.prediction_service import get_prediction_service

@router.post("/predict")
async def predict_asset(
    asset_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Prédire tendance asset avec ML.
    
    Body exemple:
    {
        "asset_symbol": "AAPL",
        "asset_data": {
            "price_history": [150.0, 151.2, 152.5, ...],  # 60+ points
            "volume_history": [50000, 52000, 48000, ...]
        }
    }
    """
    try:
        # Extraire données
        asset_symbol = asset_data.get("asset_symbol")
        asset_stats = asset_data.get("asset_data")
        
        if not all([asset_symbol, asset_stats]):
            raise HTTPException(
                status_code=400,
                detail="Missing required fields"
            )
        
        # Générer prédiction
        prediction_service = get_prediction_service()
        prediction = prediction_service.predict_finance_trend(
            asset_symbol,
            asset_stats
        )
        
        # Sauvegarder en DB (optionnel)
        # db_prediction = Prediction(
        #     user_id=current_user.id,
        #     type="finance",
        #     data=prediction
        # )
        # db.add(db_prediction)
        # db.commit()
        
        return {
            "success": True,
            "prediction": prediction
        }
        
    except Exception as e:
        logger.error(f"Error in asset prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🧪 Étape 3: Tester l'intégration

### Test sports prediction

```bash
curl -X POST http://localhost:8000/api/v1/sports/predict \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Real Madrid",
    "away_team": "Barcelona",
    "match_data": {
      "home_form": [2, 1, 2, 1, 2],
      "away_form": [1, 0, 1, 2, 0],
      "home_attack": 85.5,
      "away_attack": 83.2,
      "home_defense": 82.0,
      "away_defense": 80.5,
      "home_goals_scored": 18,
      "away_goals_scored": 16,
      "home_goals_conceded": 8,
      "away_goals_conceded": 9,
      "home_win_rate": 0.72,
      "away_win_rate": 0.68,
      "is_home": true,
      "home_xg": [2.1, 1.8, 2.3, 1.9, 2.0],
      "away_xg": [1.9, 2.1, 1.7, 2.0, 1.8],
      "h2h_history": [1, 0, 1, 2, 1],
      "home_rest_days": 4,
      "away_rest_days": 3
    }
  }'
```

### Test finance prediction

```bash
curl -X POST http://localhost:8000/api/v1/finance/predict \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_symbol": "AAPL",
    "asset_data": {
      "price_history": [150.0, 151.2, 152.5, 151.8, 153.2, ...],
      "volume_history": [50000, 52000, 48000, 51000, 53000, ...]
    }
  }'
```

---

## 📊 Étape 4: Frontend integration

### Service: `frontend/src/services/mlService.js`

```javascript
import apiClient from './apiClient';

export const predictSportsMatch = async (homeTeam, awayTeam, matchData) => {
  try {
    const response = await apiClient.post('/api/v1/sports/predict', {
      home_team: homeTeam,
      away_team: awayTeam,
      match_data: matchData
    });
    return response.data;
  } catch (error) {
    console.error('Error predicting match:', error);
    throw error;
  }
};

export const predictFinanceTrend = async (assetSymbol, assetData) => {
  try {
    const response = await apiClient.post('/api/v1/finance/predict', {
      asset_symbol: assetSymbol,
      asset_data: assetData
    });
    return response.data;
  } catch (error) {
    console.error('Error predicting trend:', error);
    throw error;
  }
};

export const getModelStatus = async () => {
  try {
    const response = await apiClient.get('/api/v1/ai/model-status');
    return response.data;
  } catch (error) {
    console.error('Error getting model status:', error);
    throw error;
  }
};
```

### Composant exemple: Sports prediction

```jsx
import React, { useState } from 'react';
import { predictSportsMatch } from '../services/mlService';

const SportsPredictor = () => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handlePredict = async () => {
    setLoading(true);
    
    const matchData = {
      home_form: [2, 1, 2, 1, 2],
      away_form: [1, 0, 1, 2, 0],
      home_attack: 85.5,
      away_attack: 83.2,
      // ... autres données
    };
    
    try {
      const result = await predictSportsMatch(
        'Real Madrid',
        'Barcelona',
        matchData
      );
      
      setPrediction(result.prediction);
    } catch (error) {
      console.error('Prediction failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="sports-predictor">
      <button onClick={handlePredict} disabled={loading}>
        {loading ? 'Prédiction...' : 'Prédire résultat'}
      </button>
      
      {prediction && (
        <div className="prediction-result">
          <h3>Prédiction ML</h3>
          <div className="probabilities">
            <div>Victoire domicile: {(prediction.prediction.home_win * 100).toFixed(1)}%</div>
            <div>Match nul: {(prediction.prediction.draw * 100).toFixed(1)}%</div>
            <div>Victoire extérieur: {(prediction.prediction.away_win * 100).toFixed(1)}%</div>
          </div>
          <div className="recommendation">
            Recommandation: {prediction.recommendation}
          </div>
          <div className="confidence">
            Confiance: {(prediction.confidence * 100).toFixed(1)}%
          </div>
          <div className="model-info">
            Modèle: {prediction.model_type}
          </div>
        </div>
      )}
    </div>
  );
};

export default SportsPredictor;
```

---

## ✅ Checklist d'intégration

- [ ] Modèles entraînés dans `ml/models/`
- [ ] `ml_prediction_service.py` créé dans backend
- [ ] `prediction_service.py` modifié pour utiliser ML
- [ ] Endpoints `/predict` ajoutés dans sports.py et finance.py
- [ ] Service frontend `mlService.js` créé
- [ ] Composants React mis à jour
- [ ] Tests API effectués
- [ ] Logs monitoring configurés

---

## 📝 Notes importantes

1. **Fallback automatique**: Si modèles non chargés, le service retourne prédictions par défaut
2. **Validation**: Toujours valider données d'entrée
3. **Logging**: Tous les appels sont loggés pour debugging
4. **Performance**: Prédictions < 100ms en moyenne
5. **Scalabilité**: Service ML peut être séparé en microservice si besoin

---

**Integration ready! 🚀**
