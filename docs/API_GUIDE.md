# Guide API - PredictWise

Base URL : `http://localhost:5000/api/v1`

Documentation interactive : `http://localhost:5000/api/docs`

---

## Authentification

### Inscription

**Endpoint** : `POST /auth/signup`

**Body** :
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Réponse** :
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "created_at": "2025-12-09T10:00:00"
  }
}
```

### Connexion

**Endpoint** : `POST /auth/login`

**Body** :
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Réponse** : Identique à signup

### Profil utilisateur

**Endpoint** : `GET /auth/me`

**Headers** :
```
Authorization: Bearer {access_token}
```

**Réponse** :
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    ...
  }
}
```

---

## Module Sports

### Liste des matchs

**Endpoint** : `GET /sports/matches`

**Query params** :
- `sport` : Type de sport (football, basketball, etc.)
- `date` : Date au format YYYY-MM-DD
- `league` : Nom de la ligue

**Exemple** : `/sports/matches?sport=football&league=Premier%20League`

**Réponse** :
```json
{
  "sport": "football",
  "matches": [
    {
      "id": 1,
      "home_team": "Team A",
      "away_team": "Team B",
      "date": "2025-12-15",
      "time": "20:00",
      "league": "Premier League",
      "odds": {
        "home": 1.85,
        "draw": 3.50,
        "away": 4.20
      }
    }
  ],
  "count": 1
}
```

### Statistiques d'équipe

**Endpoint** : `GET /sports/statistics/{team_name}`

**Query params** :
- `sport` : Type de sport

**Exemple** : `/sports/statistics/Manchester%20United?sport=football`

**Réponse** :
```json
{
  "team": "Manchester United",
  "sport": "football",
  "statistics": {
    "matches_played": 38,
    "wins": 25,
    "draws": 8,
    "losses": 5,
    "goals_for": 78,
    "goals_against": 32,
    "win_rate": 0.658
  }
}
```

### Prédiction de match

**Endpoint** : `POST /sports/predict`

**Body** :
```json
{
  "team_home": "Team A",
  "team_away": "Team B",
  "sport": "football",
  "features": {}
}
```

**Réponse** :
```json
{
  "prediction": {
    "result": "HOME_WIN",
    "confidence": 0.72,
    "probabilities": {
      "home_win": 0.65,
      "draw": 0.20,
      "away_win": 0.15
    },
    "model_version": "v1.0"
  },
  "prediction_id": 42
}
```

---

## Module Finance

### Données boursières

**Endpoint** : `GET /finance/stocks/{symbol}`

**Query params** :
- `period` : 1d, 5d, 1mo, 3mo, 1y
- `interval` : 1m, 5m, 1h, 1d

**Exemple** : `/finance/stocks/AAPL?period=1mo&interval=1d`

**Réponse** :
```json
{
  "symbol": "AAPL",
  "period": "1mo",
  "data": [
    {
      "date": "2025-11-09",
      "open": 150.23,
      "high": 152.45,
      "low": 149.80,
      "close": 151.67,
      "volume": 45678900
    },
    ...
  ]
}
```

### Indicateurs techniques

**Endpoint** : `GET /finance/indicators/{symbol}`

**Query params** :
- `period` : Période pour calcul
- `indicators` : Liste séparée par virgules (MA,RSI,VOLATILITY)

**Exemple** : `/finance/indicators/AAPL?period=1mo&indicators=MA,RSI`

**Réponse** :
```json
{
  "symbol": "AAPL",
  "indicators": {
    "MA_20": 150.45,
    "MA_50": 148.32,
    "RSI": 58.67,
    "volatility": 0.25
  }
}
```

### Prédiction de tendance

**Endpoint** : `POST /finance/predict`

**Body** :
```json
{
  "symbol": "AAPL",
  "period": "1mo"
}
```

**Réponse** :
```json
{
  "prediction": {
    "trend": "UP",
    "confidence": 0.68,
    "model_version": "v1.0"
  },
  "prediction_id": 43
}
```

### Historique des prédictions

**Endpoint** : `GET /finance/predictions/history`

**Réponse** :
```json
{
  "predictions": [
    {
      "id": 43,
      "user_id": 1,
      "prediction_type": "finance",
      "prediction_result": "UP",
      "confidence_score": 0.68,
      "model_version": "v1.0",
      "created_at": "2025-12-09T14:30:00"
    }
  ],
  "count": 1
}
```

---

## Codes d'erreur

- `200` : Succès
- `201` : Créé avec succès
- `400` : Requête invalide (données manquantes/incorrectes)
- `401` : Non authentifié (token manquant/invalide)
- `404` : Ressource non trouvée
- `500` : Erreur serveur

---

## Exemples d'utilisation avec curl

### Signup
```bash
curl -X POST http://localhost:5000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"test123"}'
```

### Login
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'
```

### Prédiction (avec token)
```bash
curl -X POST http://localhost:5000/api/v1/finance/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"symbol":"AAPL","period":"1mo"}'
```
