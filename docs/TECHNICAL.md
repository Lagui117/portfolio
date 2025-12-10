# Documentation Technique - PredictWise

## Table des matières
1. [Architecture globale](#architecture-globale)
2. [Backend](#backend)
3. [Frontend](#frontend)
4. [Machine Learning](#machine-learning)
5. [Base de données](#base-de-données)
6. [Sécurité](#sécurité)

---

## Architecture globale

PredictWise suit une architecture **client-serveur** avec séparation des préoccupations :

- **Frontend (React)** : Interface utilisateur, gestion de l'état, appels API
- **Backend (Flask)** : API REST, logique métier, accès aux données
- **ML (scikit-learn)** : Modèles de prédiction pré-entraînés
- **Base de données (SQLite)** : Stockage persistant

### Flux de données

```
User -> Frontend -> API Backend -> Services -> Models/DB
                                 -> ML Models
```

---

## Backend

### Structure

```
backend/app/
├── api/v1/          # Endpoints API versionnés
├── core/            # Configuration, DB
├── models/          # Modèles SQLAlchemy (User, Prediction, Consultation)
├── services/        # Logique métier (SportsService, FinanceService)
├── utils/           # Helpers (auth, etc.)
└── main.py          # Point d'entrée
```

### Modèles de données

**User**
- id, email, username, password_hash
- first_name, last_name
- is_active, created_at, updated_at

**Prediction**
- id, user_id, prediction_type (sports/finance)
- input_data (JSON), prediction_result
- confidence_score, model_version

**Consultation**
- id, user_id, consultation_type
- query_params, endpoint, created_at

### Services

**SportsService**
- Récupération de matchs via API externe
- Statistiques d'équipes
- Chargement du modèle ML pour prédictions

**FinanceService**
- Récupération de données boursières
- Calcul d'indicateurs techniques
- Prédiction de tendances

### Authentification

- JWT (JSON Web Tokens)
- Token stocké côté client (localStorage)
- Middleware de vérification sur routes protégées
- Expiration configurable (défaut : 1h)

---

## Frontend

### Structure

```
frontend/src/
├── components/      # Navbar, PrivateRoute
├── pages/           # Home, Login, Signup, Dashboard, Sports, Finance
├── context/         # AuthContext (gestion utilisateur)
├── services/        # api.js (client axios)
├── hooks/           # useAuth
└── App.jsx          # Router principal
```

### Gestion de l'état

- **AuthContext** : État global de l'authentification
- **useState/useEffect** : État local des composants
- Pas de Redux (architecture simple)

### Routes

- `/` - Page d'accueil publique
- `/login` - Connexion
- `/signup` - Inscription
- `/dashboard` - Tableau de bord (protégé)
- `/sports` - Module sports (protégé)
- `/finance` - Module finance (protégé)

### API Client

Axios configuré avec :
- Base URL : `/api/v1`
- Intercepteur pour ajouter le token JWT
- Gestion des erreurs 401 (redirection login)

---

## Machine Learning

### Modèle Sports

**Algorithme** : Random Forest Classifier

**Features** :
- Statistiques d'équipe (victoires, défaites)
- Moyennes de buts
- Forme récente
- Historique face-à-face

**Target** : HOME_WIN (2) / DRAW (1) / AWAY_WIN (0)

**Performance** : Accuracy ~65-70% (dummy data)

### Modèle Finance

**Algorithme** : Logistic Regression

**Features** :
- Moving Averages (MA_5, MA_20)
- RSI (Relative Strength Index)
- Volatilité

**Target** : UP (1) / DOWN (0)

**Preprocessing** : StandardScaler pour normalisation

**Performance** : Accuracy ~55-60% (dummy data)

### Entraînement

```bash
cd ml/scripts
python train_sports_model.py    # Génère sports_model.pkl
python train_finance_model.py   # Génère finance_model.pkl + scaler
```

Les modèles sont chargés au démarrage du backend.

---

## Base de données

### Schéma SQLite

**users**
- PK: id
- UK: email, username
- Relations: predictions, consultations

**predictions**
- PK: id
- FK: user_id -> users.id
- Index: prediction_type, created_at

**consultations**
- PK: id
- FK: user_id -> users.id
- Index: consultation_type, created_at

### Migrations

SQLAlchemy crée automatiquement les tables avec `db.create_all()`.

Pour production, utiliser Alembic :
```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

---

## Sécurité

### Backend
- Hachage des mots de passe avec `bcrypt`
- Tokens JWT signés avec secret key
- CORS configuré (whitelist frontend)
- Validation des entrées
- SQL injection protégé (ORM)

### Frontend
- Token stocké en localStorage (alternative : httpOnly cookies)
- Routes protégées avec PrivateRoute
- Redirection automatique si non authentifié

### Recommandations production
- HTTPS obligatoire
- Secrets dans variables d'environnement
- Rate limiting sur l'API
- Monitoring des logs
- Backup régulier de la DB

---

## API Externe

### Sports
- Utiliser API-Sports.io ou similaire
- Nécessite une clé API (variable `SPORTS_API_KEY`)

### Finance
- Yahoo Finance API (yfinance) ou Alpha Vantage
- Gratuit avec limitations

---

## Performance

### Backend
- Cache Redis pour requêtes fréquentes (à implémenter)
- Pagination des résultats
- Indexation DB sur colonnes fréquemment filtrées

### Frontend
- Code splitting avec React.lazy
- Optimisation des images
- Debounce sur recherches

---

## Déploiement

### Backend
- Gunicorn comme serveur WSGI
- Nginx comme reverse proxy
- Variables d'environnement via fichier .env

### Frontend
- Build : `npm run build`
- Servir via Nginx ou CDN

### ML
- Modèles versionnés et stockés avec le backend
- Réentraînement périodique avec nouvelles données

---

**Date de dernière mise à jour** : 9 décembre 2025
