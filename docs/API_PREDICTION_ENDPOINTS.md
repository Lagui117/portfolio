# API Endpoints de Prédiction - PredictWise

## Vue d'ensemble

Les nouveaux endpoints de prédiction combinent trois sources de données pour fournir des analyses complètes :
1. **Données API externes** (sports/finance)
2. **Modèle ML interne** (prédiction basée sur les données)
3. **Analyse GPT** (insights générés par IA)

⚠️ **IMPORTANT**: Ces endpoints sont à but **STRICTEMENT ÉDUCATIF**. Ne pas utiliser pour des paris ou investissements réels.

---

## Endpoints Sports

### GET /api/v1/sports/predict/{match_id}

Génère une prédiction complète pour un match sportif.

#### Authentification
Requiert un token JWT Bearer dans le header `Authorization`.

#### Paramètres

**Path Parameters:**
- `match_id` (string, required): Identifiant unique du match

**Query Parameters:**
Aucun pour le moment.

#### Exemple de requête

```bash
curl -X GET "http://localhost:5000/api/v1/sports/predict/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Exemple de réponse (200 OK)

```json
{
  "match_data": {
    "match_id": "1",
    "sport": "football",
    "league": "Premier League",
    "country": "England",
    "date": "2025-12-12T15:00:00",
    "venue": "Old Trafford",
    "status": "NS",
    "home_team": {
      "id": "33",
      "name": "Manchester United",
      "recent_form": "WWDWL",
      "goals_scored_avg": 1.8,
      "goals_conceded_avg": 1.2,
      "win_rate": 0.65
    },
    "away_team": {
      "id": "40",
      "name": "Liverpool",
      "recent_form": "WWWDW",
      "goals_scored_avg": 2.3,
      "goals_conceded_avg": 0.9,
      "win_rate": 0.75
    },
    "odds": {
      "home_win": 2.80,
      "draw": 3.40,
      "away_win": 2.50
    }
  },
  "ml_prediction": {
    "prediction": "AWAY_WIN",
    "probabilities": {
      "HOME_WIN": 0.32,
      "DRAW": 0.21,
      "AWAY_WIN": 0.47
    },
    "confidence": 0.47,
    "model_used": "RandomForest"
  },
  "gpt_analysis": {
    "domain": "sports",
    "summary": "Liverpool part favori avec 47% de chances de victoire selon notre modèle",
    "analysis": "L'analyse des statistiques récentes montre que Liverpool est en meilleure forme avec 4 victoires sur les 5 derniers matchs. Leur efficacité offensive (2.3 buts/match) surpasse celle de Manchester United (1.8). Cependant, le facteur domicile et l'historique récent des confrontations directes montrent un équilibre relatif...",
    "prediction_type": "probability",
    "prediction_value": 0.47,
    "confidence": 0.68,
    "caveats": "Les performances passées ne garantissent pas les résultats futurs. De nombreux facteurs imprévisibles peuvent influencer le match (blessures, conditions météo, décisions arbitrales).",
    "educational_reminder": "Cette analyse est purement éducative et expérimentale. Elle ne doit en aucun cas servir de base pour des paris sportifs."
  },
  "disclaimer": {
    "warning": "ATTENTION: Cette plateforme est strictement ÉDUCATIVE",
    "message": "Les prédictions sont expérimentales et ne doivent PAS être utilisées pour des paris réels.",
    "reminder": "PredictWise est un outil d'apprentissage pour comprendre les données sportives."
  },
  "metadata": {
    "match_id": "1",
    "prediction_id": 42,
    "timestamp": "2025-12-10T14:30:00"
  }
}
```

#### Codes de réponse

- `200 OK`: Prédiction générée avec succès
- `401 Unauthorized`: Token JWT manquant ou invalide
- `404 Not Found`: Match introuvable
- `500 Internal Server Error`: Erreur serveur

---

## Endpoints Finance

### GET /api/v1/finance/predict/{ticker}

Génère une prédiction complète pour un actif financier.

#### Authentification
Requiert un token JWT Bearer dans le header `Authorization`.

#### Paramètres

**Path Parameters:**
- `ticker` (string, required): Symbole boursier (ex: AAPL, GOOGL, MSFT)

**Query Parameters:**
- `period` (string, optional): Période d'analyse. Défaut: `1mo`
  - Valeurs possibles: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`

#### Exemple de requête

```bash
curl -X GET "http://localhost:5000/api/v1/finance/predict/AAPL?period=1mo" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Exemple de réponse (200 OK)

```json
{
  "stock_data": {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "currency": "USD",
    "exchange": "NASDAQ",
    "market_cap": 3000000000000,
    "current_price": 185.50,
    "price_change_pct": 1.25,
    "indicators": {
      "MA_5": 183.20,
      "MA_20": 180.50,
      "MA_50": 175.80,
      "RSI": 58.3,
      "volatility_daily": 0.0185,
      "volatility_annual": 0.293,
      "avg_volume": 52000000,
      "current_volume": 48000000
    },
    "historical_data": {
      "period": "2025-11-10 to 2025-12-10",
      "data_points": 30,
      "high": 190.25,
      "low": 178.50,
      "avg_close": 183.75
    },
    "timestamp": "2025-12-10T14:35:00"
  },
  "ml_prediction": {
    "prediction": "UP",
    "probabilities": {
      "UP": 0.64,
      "DOWN": 0.36
    },
    "confidence": 0.64,
    "model_used": "LogisticRegression"
  },
  "gpt_analysis": {
    "domain": "finance",
    "summary": "Tendance haussière probable à court terme selon l'analyse technique",
    "analysis": "Les indicateurs techniques montrent des signaux positifs : la MA_5 est au-dessus de la MA_20, indiquant une dynamique haussière récente. Le RSI à 58.3 suggère un marché ni suracheté ni survendu, laissant de la marge de progression. La volatilité reste dans des niveaux normaux pour ce titre. Le prix actuel dépasse les moyennes mobiles clés, confirmant la tendance...",
    "prediction_type": "trend",
    "prediction_value": "UP",
    "confidence": 0.72,
    "caveats": "Cette analyse se base uniquement sur l'analyse technique et ne prend pas en compte les fondamentaux de l'entreprise, les actualités macroéconomiques, ou les événements géopolitiques qui peuvent avoir un impact majeur.",
    "educational_reminder": "Cette plateforme est éducative. Les marchés financiers comportent des risques importants de perte en capital."
  },
  "disclaimer": {
    "warning": "ATTENTION: Cette plateforme est strictement ÉDUCATIVE",
    "message": "Les prédictions sont expérimentales et ne doivent PAS être utilisées pour des investissements réels.",
    "reminder": "PredictWise est un outil d'apprentissage pour comprendre les marchés financiers.",
    "risk_warning": "Les investissements comportent des risques de perte en capital."
  },
  "metadata": {
    "ticker": "AAPL",
    "period": "1mo",
    "prediction_id": 43,
    "timestamp": "2025-12-10T14:35:00"
  }
}
```

#### Codes de réponse

- `200 OK`: Prédiction générée avec succès
- `401 Unauthorized`: Token JWT manquant ou invalide
- `404 Not Found`: Ticker introuvable ou données indisponibles
- `500 Internal Server Error`: Erreur serveur

---

## Structure de la réponse GPT

Tous les endpoints de prédiction incluent une section `gpt_analysis` avec cette structure :

```typescript
{
  domain: "sports" | "finance",
  summary: string,              // Résumé en 1-2 phrases
  analysis: string,             // Analyse détaillée (200-300 mots)
  prediction_type: "probability" | "trend",
  prediction_value: number | string,  // 0-1 pour sports, "UP"/"DOWN" pour finance
  confidence: number,           // 0-1
  caveats: string,             // Limitations de l'analyse
  educational_reminder: string, // Rappel du caractère éducatif
  ml_score?: number | string   // Score du modèle ML si disponible
}
```

---

## Gestion des erreurs

### Erreur d'API externe

Si l'API externe (sports/finance) échoue, le système utilise des données mock de secours :

```json
{
  "match_data": {
    "mock_data": true,
    ...
  }
}
```

### Erreur du modèle ML

Si le modèle ML n'est pas disponible :

```json
{
  "ml_prediction": {
    "error": "ML prediction unavailable",
    "model_used": "Fallback"
  }
}
```

### Erreur GPT

Si l'analyse GPT échoue (clé API manquante, quota dépassé, etc.) :

```json
{
  "gpt_analysis": {
    "error": "GPT analysis unavailable",
    "educational_reminder": "This is an educational platform. Do not use for real betting."
  }
}
```

---

## Configuration requise

### Variables d'environnement

#### Backend (.env)

```bash
# OBLIGATOIRE pour l'analyse GPT
OPENAI_API_KEY=sk-...

# OPTIONNEL - utilise mock data si absent
SPORTS_API_KEY=...
SPORTS_API_HOST=api-football-v1.p.rapidapi.com
USE_MOCK_SPORTS_API=false

# OPTIONNEL - utilise yfinance si absent
FINANCE_API_KEY=...
USE_MOCK_FINANCE_API=false
```

### Installation des dépendances

```bash
cd backend
pip install -r requirements.txt
```

Nouvelles dépendances ajoutées :
- `openai==1.6.1` - Client OpenAI pour GPT
- `yfinance==0.2.33` - Données financières

---

## Utilisation Frontend

### Service Sports

```javascript
import sportsService from '@/services/sportsService';

// Obtenir une prédiction complète
const prediction = await sportsService.getSportsPrediction('1');

console.log(prediction.match_data);
console.log(prediction.ml_prediction);
console.log(prediction.gpt_analysis);
```

### Service Finance

```javascript
import financeService from '@/services/financeService';

// Obtenir une prédiction complète
const prediction = await financeService.getFinancePrediction('AAPL', '1mo');

console.log(prediction.stock_data);
console.log(prediction.ml_prediction);
console.log(prediction.gpt_analysis);
```

---

## Limitations et considérations

### Performances

- **Temps de réponse** : 2-5 secondes (en raison des appels API externes + GPT)
- **Rate limiting** : Dépend de vos quotas d'API (OpenAI, Sports API, etc.)

### Coûts

- **OpenAI GPT-4o-mini** : ~$0.15 pour 1M tokens d'entrée, ~$0.60 pour 1M tokens de sortie
- Estimation : ~$0.001-0.003 par prédiction avec GPT-4o-mini
- Recommandation : Monitorer l'utilisation via le dashboard OpenAI

### Données mock

En mode développement sans clés API :
- Les données sports sont générées aléatoirement mais cohérentes
- Les données finance utilisent des valeurs réalistes pour tickers connus
- L'analyse GPT renvoie un message de fallback

### Sécurité

- Toutes les clés API doivent être dans `.env` (jamais dans le code)
- Le fichier `.env` doit être dans `.gitignore`
- Les tokens JWT expirent après 1 heure par défaut
- CORS configuré pour autoriser uniquement le frontend

---

## Monitoring et logs

Les services loggent automatiquement :
- Succès/échec des appels API externes
- Chargement des modèles ML
- Erreurs GPT
- Consultations et prédictions enregistrées en BDD

Consultez les logs pour déboguer :

```bash
# Dans le terminal où tourne le backend
tail -f logs/app.log
```

---

## Troubleshooting

### "GPT analysis unavailable"

**Cause** : `OPENAI_API_KEY` manquante ou invalide

**Solution** :
```bash
# Vérifier la variable
echo $OPENAI_API_KEY

# L'ajouter dans .env
OPENAI_API_KEY=sk-...
```

### "Match not found" / "Ticker not found"

**Cause** : Données non disponibles dans l'API externe

**Solution** : 
- Vérifier que l'ID/ticker est correct
- Activer le mode mock : `USE_MOCK_SPORTS_API=true`

### "ML prediction unavailable"

**Cause** : Modèles ML non entraînés ou fichiers manquants

**Solution** :
- Les modèles se trouvent dans `ml/models/`
- Entraîner les modèles : `cd ml && python scripts/train_sports_model.py`
- Le système utilise automatiquement un fallback si les modèles sont absents

---

## Ressources externes

### APIs recommandées

**Sports :**
- [API-FOOTBALL](https://rapidapi.com/api-sports/api/api-football) - Données football complètes
- [The Odds API](https://the-odds-api.com/) - Cotes sportives
- [SportMonks](https://www.sportmonks.com/) - Multi-sports

**Finance :**
- [yfinance](https://pypi.org/project/yfinance/) - Gratuit, Yahoo Finance
- [Alpha Vantage](https://www.alphavantage.co/) - API gratuite avec limite
- [IEX Cloud](https://iexcloud.io/) - Données en temps réel
- [Twelve Data](https://twelvedata.com/) - Multi-actifs

**IA :**
- [OpenAI Platform](https://platform.openai.com/) - GPT API
- [OpenAI Pricing](https://openai.com/pricing) - Tarification

---

## Prochaines étapes

Améliorations possibles :
- [ ] Cache Redis pour les prédictions récentes
- [ ] WebSockets pour mises à jour en temps réel
- [ ] Comparaison de plusieurs modèles ML
- [ ] Export PDF des analyses
- [ ] Historique de précision des prédictions
- [ ] Système de notifications
