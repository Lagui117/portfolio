# PredictWise API Documentation

## Base URL
```
http://localhost:5000/api/v1
```

## Interactive Documentation
Swagger UI: `http://localhost:5000/api/docs`

---

## Authentication

### Register
**POST** `/auth/register`

Créer un nouveau compte utilisateur.

**Request Body:**
```json
{
  "username": "string (3-50 chars)",
  "email": "string (valid email)",
  "password": "string (min 8 chars)"
}
```

**Response** `201 Created`:
```json
{
  "message": "User registered successfully",
  "access_token": "eyJhbGci...",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2025-12-09T15:30:00"
  }
}
```

### Login
**POST** `/auth/login`

Connexion utilisateur existant.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "mypassword"
}
```

**Response** `200 OK`:
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGci...",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "last_login": "2025-12-09T15:35:00"
  }
}
```

### Get Profile
**GET** `/auth/me`

Récupérer le profil de l'utilisateur connecté (requiert authentification).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response** `200 OK`:
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2025-12-09T15:30:00",
    "last_login": "2025-12-09T15:35:00",
    "stats": {
      "total_predictions": 42,
      "total_consultations": 156
    }
  }
}
```

### Update Profile
**PUT** `/auth/me`

Mettre à jour le profil (requiert authentification).

**Request Body:**
```json
{
  "username": "new_username",
  "current_password": "oldpass",
  "new_password": "newpass"
}
```

---

## Sports Module

### Get Upcoming Matches
**GET** `/sports/matches`

Récupérer les matchs à venir.

**Query Parameters:**
- `league` (optional): Filter by league
- `limit` (optional): Max results (default: 20)

**Response** `200 OK`:
```json
{
  "matches": [
    {
      "id": 1,
      "home_team": "Team A",
      "away_team": "Team B",
      "league": "Premier League",
      "match_date": "2025-12-15T15:00:00",
      "home_odds": 2.1,
      "draw_odds": 3.4,
      "away_odds": 3.2,
      "status": "scheduled"
    }
  ],
  "count": 10
}
```

### Get Team Statistics
**GET** `/sports/statistics/{team_name}`

Statistiques d'une équipe.

**Response** `200 OK`:
```json
{
  "team": "Team A",
  "statistics": {
    "matches_played": 25,
    "wins": 15,
    "draws": 5,
    "losses": 5,
    "win_rate": 0.60,
    "avg_goals_scored": 2.1,
    "avg_goals_conceded": 1.2,
    "recent_form": 2.2
  }
}
```

### Predict Match Outcome
**POST** `/sports/predict`

Prédiction ML du résultat d'un match.

**Request Body:**
```json
{
  "home_team": "Team A",
  "away_team": "Team B",
  "league": "Premier League"
}
```

**Response** `200 OK`:
```json
{
  "prediction": {
    "outcome": "HOME_WIN",
    "confidence": 0.68,
    "probabilities": {
      "HOME_WIN": 0.68,
      "DRAW": 0.20,
      "AWAY_WIN": 0.12
    },
    "model_version": "v1.0"
  },
  "prediction_id": 123,
  "timestamp": "2025-12-09T15:40:00"
}
```

### Get Prediction History
**GET** `/sports/history`

Historique des prédictions de l'utilisateur.

**Query Parameters:**
- `limit` (optional): Max results (default: 50)

---

## Finance Module

### Get Stock Data
**GET** `/finance/stocks/{symbol}`

Données historiques d'un symbole boursier.

**Query Parameters:**
- `period` (optional): 1d, 5d, 1mo, 3mo, 6mo, 1y (default: 1mo)
- `interval` (optional): 1m, 5m, 1h, 1d (default: 1d)

**Response** `200 OK`:
```json
{
  "symbol": "AAPL",
  "period": "1mo",
  "interval": "1d",
  "data": [
    {
      "date": "2025-11-09",
      "open": 175.50,
      "high": 178.20,
      "low": 174.80,
      "close": 177.30,
      "volume": 45000000
    }
  ],
  "count": 30
}
```

### Get Technical Indicators
**GET** `/finance/indicators/{symbol}`

Indicateurs techniques calculés.

**Query Parameters:**
- `period` (optional): Time period (default: 1mo)
- `indicators` (optional): MA,RSI,VOLATILITY,MACD (default: MA,RSI,VOLATILITY)

**Response** `200 OK`:
```json
{
  "symbol": "AAPL",
  "period": "1mo",
  "indicators": {
    "MA_5": 176.82,
    "MA_20": 172.45,
    "MA_50": 168.90,
    "RSI": 62.5,
    "MACD": {
      "macd_line": 2.34,
      "signal_line": 1.89
    },
    "volatility_daily": 0.018,
    "volatility_annual": 0.286,
    "current_price": 177.30
  }
}
```

### Predict Stock Trend
**POST** `/finance/predict`

Prédiction ML de la tendance du cours.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "period": "1mo"
}
```

**Response** `200 OK`:
```json
{
  "prediction": {
    "symbol": "AAPL",
    "trend": "UP",
    "confidence": 0.73,
    "probabilities": {
      "UP": 0.73,
      "DOWN": 0.27
    },
    "model_version": "v1.0"
  },
  "prediction_id": 456,
  "timestamp": "2025-12-09T15:45:00"
}
```

### Get Prediction History
**GET** `/finance/predictions/history`

Historique des prédictions financières.

**Query Parameters:**
- `limit` (optional): Max results (default: 50)

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Champ requis manquant",
  "details": "Le champ 'symbol' est requis"
}
```

### 401 Unauthorized
```json
{
  "error": "Token invalide ou expiré"
}
```

### 404 Not Found
```json
{
  "error": "Ressource non trouvée"
}
```

### 500 Internal Server Error
```json
{
  "error": "Erreur serveur interne",
  "details": "Description de l'erreur"
}
```

---

## Rate Limiting

Actuellement aucune limite. En production, implémenter:
- 100 requêtes/minute par utilisateur
- 1000 requêtes/heure par utilisateur

---

## Notes

- Tous les endpoints (sauf auth) requièrent un Bearer token
- Les timestamps sont en format ISO 8601
- Les devises sont en USD
- Les données de développement sont mockées
