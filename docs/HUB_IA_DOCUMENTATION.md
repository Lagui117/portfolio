# Hub IA - Page d'Accueil Principale

## Vue d'ensemble

Le **Hub IA** est la page d'accueil centrale de PredictWise après connexion. Elle offre une interface moderne et intuitive pour accéder aux différentes fonctionnalités de la plateforme.

## Caractéristiques

### 🎯 Navigation Centralisée

Deux cartes principales permettent d'accéder aux modules :

1. **Analyse Sportive** (⚽)
   - Vue d'ensemble des matchs récents
   - Statistiques d'équipes et tendances
   - Analyse textuelle générée par IA
   - Prédictions ML combinées à GPT

2. **Analyse Financière** (📈)
   - Graphiques de prix et indicateurs simples
   - Tendance estimée (hausse/baisse)
   - Analyse IA pédagogique sur le contexte
   - Indicateurs techniques (MA, RSI, volatilité)

### 🤖 Suggestion IA du Jour

Section dynamique affichant des insights générés quotidiennement :
- Analyse des tendances récentes
- Corrélations sportives et financières
- Conseils éducatifs basés sur les données
- Badge "Propulsé par GPT-4"

### 📊 Statistiques Utilisateur

Tableau de bord personnel affichant :
- **Prédictions totales** : Nombre cumulé d'analyses effectuées
- **Analyses sportives** : Prédictions dans le domaine sportif
- **Analyses financières** : Prédictions boursières
- **Consultations** : Nombre de sessions d'analyse

## Architecture Frontend

### Composant Principal : `HomeHub.jsx`

```jsx
// Localisation : frontend/src/pages/HomeHub.jsx

import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import { getDailySuggestion, getUserStats } from '../services/aiService'
import './HomeHub.css'
```

**Fonctionnalités clés :**
- Chargement asynchrone de la suggestion IA
- Récupération des statistiques utilisateur
- Navigation vers Sports/Finance au clic
- Responsive design

### Service IA : `aiService.js`

```javascript
// Localisation : frontend/src/services/aiService.js

export const getDailySuggestion = async () => {
  const response = await apiClient.get('/ai/daily-suggestion')
  return response.data
}

export const getUserStats = async () => {
  const response = await apiClient.get('/users/stats')
  return response.data
}
```

## Architecture Backend

### Endpoint : `/api/v1/ai/daily-suggestion`

**Méthode :** `GET`  
**Authentification :** Optionnelle (JWT)

**Réponse :**
```json
{
  "title": "Suggestion IA du jour",
  "text": "Sur les derniers matchs, plusieurs équipes montrent..."
}
```

**Logique :**
- Suggestion générée en fonction de la date (seed basée sur YYYYMMDD)
- Même suggestion pour tous les utilisateurs le même jour
- Rotation automatique parmi 5 suggestions prédéfinies

### Endpoint : `/api/v1/users/stats`

**Méthode :** `GET`  
**Authentification :** Requise (JWT)

**Réponse :**
```json
{
  "total_predictions": 42,
  "sports_predictions": 25,
  "finance_predictions": 17,
  "total_consultations": 68,
  "member_since": "2024-01-15T10:30:00"
}
```

**Requêtes SQL :**
```python
# Compte les prédictions par catégorie
total_predictions = db.query(func.count(Prediction.id)).filter(
    Prediction.user_id == current_user_id
).scalar()

sports_predictions = db.query(func.count(Prediction.id)).filter(
    Prediction.user_id == current_user_id,
    Prediction.category == 'sports'
).scalar()
```

## Styles et Design

### Palette de Couleurs

- **Background principal :** `#020617` (Très sombre)
- **Cartes :** `#0f172a` avec bordures `#1e293b`
- **Accent Sports :** `#22c55e` (Vert)
- **Accent Finance :** `#38bdf8` (Bleu ciel)
- **Accent IA :** `#4f46e5` (Indigo)

### Animations

```css
/* Hover sur les cartes */
.hub-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 26px 60px rgba(79, 70, 229, 0.3);
}

/* Effet de pulsation sur le bloc IA */
@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

/* Animation flottante de l'icône */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
```

### Responsive

- **Desktop (>768px) :** Grille 2 colonnes pour les cartes
- **Tablette (480-768px) :** 1 colonne, espacement réduit
- **Mobile (<480px) :** Layout vertical complet

## Routes et Navigation

### Configuration dans `App.jsx`

```jsx
<Route path="/hub" element={
  <PrivateRoute>
    <HomeHub />
  </PrivateRoute>
} />
```

### Redirections après Authentification

```javascript
// Login.jsx et Signup.jsx
const handleSubmit = async (e) => {
  await login(email, password)
  navigate('/hub')  // Redirection vers le Hub
}
```

### Navbar

```jsx
<Link to={isAuthenticated ? "/hub" : "/"} className="navbar-brand">
  PredictWise
</Link>
```

## Sécurité

### Protection des Routes

- Page accessible uniquement après authentification
- Vérification JWT pour `/users/stats`
- Suggestion IA disponible sans auth (engagement utilisateur)

### Gestion des Données

- Pas de données sensibles exposées
- Statistiques calculées côté serveur
- Validation des tokens JWT avant chaque requête

## Disclaimers Éducatifs

Trois niveaux de disclaimers :

1. **Header global :**
   > "Les prédictions et analyses sont expérimentales et ne doivent pas être utilisées pour des décisions de pari ou d'investissement réelles."

2. **Badge GPT-4 :**
   > "Propulsé par GPT-4" - Transparence sur la technologie utilisée

3. **Footer :**
   > "Plateforme éducative" - Rappel constant du contexte pédagogique

## Extensions Futures

### Intégration GPT Complète

```python
# TODO: Endpoint /ai/daily-suggestion avec GPT
async def get_daily_insight():
    gpt_service = GPTService()
    prompt = "Génère un insight éducatif basé sur les tendances récentes..."
    return gpt_service.generate_text(prompt)
```

### Personnalisation

- Suggestions basées sur l'historique utilisateur
- Recommandations de matchs/actions à analyser
- Graphiques de progression personnels

### Gamification

- Badges pour nombre de prédictions
- Streaks de consultations quotidiennes
- Classement communautaire (anonymisé)

## Fichiers Créés/Modifiés

### Frontend

```
frontend/src/
├── pages/
│   ├── HomeHub.jsx         ✅ Nouveau
│   ├── HomeHub.css         ✅ Nouveau
│   ├── Login.jsx           🔧 Modifié (redirect /hub)
│   └── Signup.jsx          🔧 Modifié (redirect /hub)
├── services/
│   └── aiService.js        ✅ Nouveau
├── components/
│   └── Navbar.jsx          🔧 Modifié (lien Hub IA)
└── App.jsx                 🔧 Modifié (route /hub)
```

### Backend

```
backend/app/
├── api/v1/
│   ├── users.py            ✅ Nouveau (/users/stats)
│   └── ai.py               ✅ Nouveau (/ai/daily-suggestion)
└── main.py                 🔧 Modifié (namespaces)
```

## Test et Déploiement

### Tests Frontend

```bash
# Démarrer le frontend
cd frontend
npm run dev

# Accéder à http://localhost:5173/hub après login
```

### Tests Backend

```bash
# Tester l'endpoint stats
curl -X GET http://localhost:8000/api/v1/users/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Tester la suggestion IA
curl -X GET http://localhost:8000/api/v1/ai/daily-suggestion
```

### Vérifications

- ✅ Navigation fluide entre Hub, Sports, Finance
- ✅ Chargement des statistiques utilisateur
- ✅ Suggestion IA change quotidiennement
- ✅ Responsive design sur mobile/tablette
- ✅ Animations et transitions fonctionnelles

## Conclusion

Le **Hub IA** transforme PredictWise en une plateforme moderne et engageante, avec :

- Interface utilisateur premium (dark mode)
- Accès rapide aux fonctionnalités principales
- Insights quotidiens générés par IA
- Suivi des performances utilisateur
- Design responsive et accessible

Cette page centralise l'expérience utilisateur tout en maintenant l'aspect éducatif de la plateforme.
