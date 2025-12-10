# Intégration OpenAI & APIs - PredictWise

## Vue d'ensemble

Cette mise à jour ajoute l'analyse par intelligence artificielle (GPT) et l'intégration d'APIs externes pour les données sportives et financières.

### Nouvelles fonctionnalités

#### 1. Analyse GPT (OpenAI)
- Analyse textuelle structurée des prédictions
- Insights et explications pédagogiques
- Format JSON standardisé
- Fallback automatique si GPT indisponible

#### 2. APIs Sports
- Intégration API-FOOTBALL (RapidAPI)
- Support The Odds API
- Données réelles de matchs, stats, cotes
- Mode mock pour développement sans API

#### 3. APIs Finance
- Support yfinance (Yahoo Finance, gratuit)
- Support Alpha Vantage
- Support IEX Cloud
- Indicateurs techniques calculés automatiquement

#### 4. Endpoints de prédiction
- `/api/v1/sports/predict/{match_id}` - Prédiction sportive complète
- `/api/v1/finance/predict/{ticker}` - Prédiction financière complète

Chaque endpoint combine :
1. Données API externes
2. Prédiction ML interne
3. Analyse GPT

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                       │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │  SportsPage.jsx      │  │    FinancePage.jsx           │ │
│  │  - Match ID input    │  │    - Ticker input            │ │
│  │  - Display results   │  │    - Display results         │ │
│  └──────────┬───────────┘  └──────────┬───────────────────┘ │
└─────────────┼──────────────────────────┼─────────────────────┘
              │                          │
              │  sportsService.js        │  financeService.js
              │                          │
┌─────────────┴──────────────────────────┴─────────────────────┐
│                     Backend API (Flask)                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              API Endpoints (v1)                        │  │
│  │  - POST /sports/predict/{id}                           │  │
│  │  - POST /finance/predict/{ticker}                      │  │
│  └───┬────────────────────────────────────────┬───────────┘  │
│      │                                        │              │
│  ┌───▼──────────┐  ┌────────────┐  ┌────────▼──────────┐  │
│  │ Sports API   │  │  GPT       │  │ Finance API       │  │
│  │ Service      │  │  Service   │  │ Service           │  │
│  │              │  │            │  │                   │  │
│  │ - get_match  │  │ - analyse_ │  │ - get_stock_data │  │
│  │   _data()    │  │   sport()  │  │ - get_indicators │  │
│  │ - Mock mode  │  │ - analyse_ │  │ - Mock mode      │  │
│  │              │  │   finance()│  │                   │  │
│  └───┬──────────┘  └────┬───────┘  └────────┬──────────┘  │
│      │                  │                    │              │
│  ┌───▼──────────────────▼────────────────────▼──────────┐  │
│  │           Prediction Service (ML)                     │  │
│  │  - predict_sport_event()                              │  │
│  │  - predict_stock_movement()                           │  │
│  │  - Load ML models (sports_model.pkl, finance_model)   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
              │                  │                    │
              ▼                  ▼                    ▼
     ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐
     │ External APIs  │  │  OpenAI API  │  │  Database       │
     │ - API-Football │  │  (GPT-4o-mini│  │  - Predictions  │
     │ - The Odds API │  │   /GPT-3.5)  │  │  - Consultations│
     │ - yfinance     │  │              │  │  - Users        │
     │ - Alpha Vantage│  │              │  │                 │
     └────────────────┘  └──────────────┘  └─────────────────┘
```

---

## Fichiers créés/modifiés

### Nouveaux fichiers backend

```
backend/
├── app/
│   └── services/
│       ├── gpt_service.py              # Service OpenAI GPT ✨ NOUVEAU
│       ├── sports_api_service.py       # Service API sports ✨ NOUVEAU
│       └── finance_api_service.py      # Service API finance ✨ NOUVEAU
├── .env.example                        # Template variables d'env ✨ MODIFIÉ
└── requirements.txt                    # + openai==1.6.1 ✨ MODIFIÉ
```

### Fichiers backend modifiés

```
backend/app/api/v1/
├── sports.py    # + Endpoint /predict/{match_id} + imports
└── finance.py   # + Endpoint /predict/{ticker} + imports
```

### Nouveaux fichiers frontend

```
frontend/
├── .env.example                  # Template variables d'env ✨ MODIFIÉ
└── src/services/
    ├── sportsService.js          # + getSportsPrediction() ✨ MODIFIÉ
    └── financeService.js         # + getFinancePrediction() ✨ MODIFIÉ
```

### Documentation

```
docs/
├── API_PREDICTION_ENDPOINTS.md    # Documentation API complète ✨ NOUVEAU
└── INSTALLATION_OPENAI.md         # Guide d'installation ✨ NOUVEAU
```

---

## Démarrage rapide

### 1. Backend

```bash
cd backend

# Installer les nouvelles dépendances
pip install openai==1.6.1 yfinance==0.2.33

# Configurer .env
cp .env.example .env
nano .env  # Ajouter OPENAI_API_KEY=sk-...

# Lancer
python app/main.py
```

### 2. Frontend

```bash
cd frontend

# Vérifier la configuration
cat .env  # VITE_API_BASE_URL=http://localhost:5000/api/v1

# Lancer
npm run dev
```

### 3. Tester

```bash
# Créer un compte
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"Test1234"}'

# Prédiction sports (remplacer TOKEN)
curl http://localhost:5000/api/v1/sports/predict/1 \
  -H "Authorization: Bearer TOKEN"

# Prédiction finance
curl http://localhost:5000/api/v1/finance/predict/AAPL \
  -H "Authorization: Bearer TOKEN"
```

---

## Configuration minimale

### Variables d'environnement obligatoires

```bash
# backend/.env
OPENAI_API_KEY=sk-...          # Obligatoire pour GPT
SECRET_KEY=...                  # Obligatoire
JWT_SECRET_KEY=...             # Obligatoire
```

### Variables optionnelles (mode mock par défaut)

```bash
# APIs externes (optionnel)
SPORTS_API_KEY=...
FINANCE_API_KEY=...

# Activer mode mock
USE_MOCK_SPORTS_API=true
USE_MOCK_FINANCE_API=false  # yfinance est gratuit
```

---

## Fonctionnement

### Flux d'une prédiction sportive

```
1. Frontend : Utilisateur entre match ID "1"
   ↓
2. sportsService.getSportsPrediction('1')
   ↓
3. GET /api/v1/sports/predict/1
   ↓
4. Backend : sports_api_service.get_match_data('1')
   → Appel API externe OU mock data
   ↓
5. Backend : prediction_service.predict_sport_event(...)
   → Modèle ML ou fallback
   ↓
6. Backend : gpt_service.analyse_sport(match_data, ml_score)
   → Appel OpenAI GPT
   ↓
7. Backend : Sauvegarder prediction en BDD
   ↓
8. Backend : Retourner JSON combiné
   ↓
9. Frontend : Afficher résultats
```

### Format de réponse

```json
{
  "match_data": { /* Infos du match */ },
  "ml_prediction": {
    "prediction": "AWAY_WIN",
    "probabilities": {"HOME_WIN": 0.32, "DRAW": 0.21, "AWAY_WIN": 0.47},
    "confidence": 0.47
  },
  "gpt_analysis": {
    "summary": "Liverpool favori...",
    "analysis": "Analyse détaillée...",
    "confidence": 0.68,
    "caveats": "Limitations...",
    "educational_reminder": "Plateforme éducative..."
  },
  "disclaimer": { /* Avertissements */ },
  "metadata": { /* IDs, timestamps */ }
}
```

---

## Coûts estimés

### OpenAI (GPT-4o-mini)

- **Prix** : $0.15/1M tokens entrée, $0.60/1M tokens sortie
- **Par prédiction** : ~500-1000 tokens → ~$0.001-0.003
- **100 prédictions** : ~$0.10-0.30
- **1000 prédictions** : ~$1-3

### APIs Sports

- **API-FOOTBALL** : 100 requêtes/jour gratuit
- **The Odds API** : 500 requêtes/mois gratuit
- **Mode mock** : Gratuit, données simulées

### APIs Finance

- **yfinance** : Gratuit (Yahoo Finance)
- **Alpha Vantage** : 500 requêtes/jour gratuit
- **IEX Cloud** : 50k requêtes/mois gratuit

---

## Sécurité

### ✅ Bonnes pratiques implémentées

- Clés API dans `.env` (jamais en dur)
- `.env` dans `.gitignore`
- Tokens JWT avec expiration
- CORS configuré
- Validation des entrées
- Logs des erreurs

### ⚠️ Points d'attention

- Limiter les appels API (rate limiting)
- Monitorer les coûts OpenAI
- Sauvegarder les prédictions (audit)
- Disclaimers éducatifs obligatoires

---

## Avertissements

### 🎓 Plateforme éducative

**PredictWise est strictement à but pédagogique.**

- Ne PAS utiliser pour des paris sportifs réels
- Ne PAS utiliser pour des investissements financiers réels
- Les prédictions sont expérimentales
- Les données passées ne garantissent pas les résultats futurs

### 📊 Précision des modèles

- Les modèles ML sont entraînés sur des données limitées
- La précision varie selon les cas
- Nombreux facteurs imprévisibles
- L'analyse GPT est informative, pas prescriptive

---

## Support

### Documentation

- [API Endpoints](./API_PREDICTION_ENDPOINTS.md) - Documentation API complète
- [Installation](./INSTALLATION_OPENAI.md) - Guide d'installation détaillé
- [API Spec](./API_SPEC.md) - Spécifications API générales

### Ressources externes

- [OpenAI Platform](https://platform.openai.com/)
- [API-FOOTBALL](https://www.api-football.com/)
- [yfinance](https://pypi.org/project/yfinance/)

### Troubleshooting

Voir [INSTALLATION_OPENAI.md](./INSTALLATION_OPENAI.md#problèmes-courants)

---

## Prochaines étapes

### Améliorations recommandées

1. **Cache Redis** - Réduire les appels API répétés
2. **WebSockets** - Updates en temps réel
3. **Historique de précision** - Tracker la performance des modèles
4. **Export PDF** - Rapports d'analyse téléchargeables
5. **Notifications** - Alertes sur événements importants

### Extensions possibles

- Support d'autres sports (basketball, tennis, etc.)
- Cryptomonnaies et Forex
- Analyse de sentiment (news, réseaux sociaux)
- Modèles ML plus sophistiqués (deep learning)
- Interface de comparaison de modèles

---

## Licence et utilisation

Ce projet est à but éducatif. Toute utilisation commerciale ou pour des décisions financières/paris réels est strictement déconseillée et se fait aux risques et périls de l'utilisateur.

---

**Version** : 1.0.0  
**Date** : Décembre 2025  
**Auteur** : PredictWise Team
