# Plan de développement PredictWise

## Objectif
Construire un MVP fonctionnel de la plateforme PredictWise en 15 étapes progressives.

---

## Étape 1 : Setup de l'environnement backend

**Objectif** : Préparer l'environnement Python et installer les dépendances.

**Actions** :
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Validation** : Aucune erreur d'installation.

**Pourquoi** : Avoir un environnement isolé pour éviter les conflits de versions.

---

## Étape 2 : Configuration de base backend

**Objectif** : Configurer les variables d'environnement et tester la connexion DB.

**Actions** :
1. Copier `.env.example` vers `.env`
2. Modifier les valeurs (SECRET_KEY, JWT_SECRET_KEY)
3. Lancer le serveur : `python app/main.py`

**Validation** : Serveur démarre sur http://localhost:5000, DB créée.

**Pourquoi** : Vérifier que la configuration de base fonctionne avant d'ajouter des fonctionnalités.

---

## Étape 3 : Test des endpoints d'authentification

**Objectif** : Vérifier que signup/login fonctionnent.

**Actions** :
1. Ouvrir http://localhost:5000/api/docs
2. Tester `POST /api/v1/auth/signup` avec des données valides
3. Tester `POST /api/v1/auth/login`
4. Copier le token JWT retourné

**Validation** : Token JWT reçu, utilisateur créé en DB.

**Pourquoi** : L'authentification est la base de toutes les fonctionnalités protégées.

---

## Étape 4 : Setup frontend

**Objectif** : Installer et lancer l'application React.

**Actions** :
```bash
cd frontend
npm install
npm run dev
```

**Validation** : Application accessible sur http://localhost:5173.

**Pourquoi** : Vérifier que l'environnement frontend est opérationnel.

---

## Étape 5 : Connexion frontend-backend

**Objectif** : Tester l'authentification via l'interface.

**Actions** :
1. Aller sur http://localhost:5173/signup
2. Créer un compte
3. Se connecter via /login
4. Vérifier la redirection vers /dashboard

**Validation** : Token stocké dans localStorage, user affiché dans Navbar.

**Pourquoi** : Valider que la communication frontend-backend fonctionne.

---

## Étape 6 : Endpoints Sports - Données mock

**Objectif** : Implémenter la récupération de matchs (données fictives).

**Actions** :
1. Tester `GET /api/v1/sports/matches` via Swagger
2. Vérifier que les données mock sont retournées
3. Aller sur /sports dans le frontend
4. Vérifier l'affichage des matchs

**Validation** : Liste de matchs affichée correctement.

**Pourquoi** : Valider la structure avant d'intégrer une vraie API.

---

## Étape 7 : Endpoints Finance - Données mock

**Objectif** : Implémenter la récupération de données boursières.

**Actions** :
1. Tester `GET /api/v1/finance/stocks/AAPL` via Swagger
2. Tester `GET /api/v1/finance/indicators/AAPL`
3. Aller sur /finance dans le frontend
4. Rechercher une action (ex: AAPL)

**Validation** : Données et indicateurs affichés.

**Pourquoi** : Structurer le module finance avant données réelles.

---

## Étape 8 : Entraînement modèle ML Sports

**Objectif** : Générer le premier modèle de prédiction sportive.

**Actions** :
```bash
cd ml
pip install -r requirements.txt
cd scripts
python train_sports_model.py
```

**Validation** : Fichier `ml/models/sports_model.pkl` créé.

**Pourquoi** : Avoir un modèle fonctionnel pour tester les prédictions.

---

## Étape 9 : Entraînement modèle ML Finance

**Objectif** : Générer le modèle de prédiction financière.

**Actions** :
```bash
cd ml/scripts
python train_finance_model.py
```

**Validation** : Fichiers `finance_model.pkl` et `finance_scaler.pkl` créés.

**Pourquoi** : Disposer d'un modèle pour les prédictions financières.

---

## Étape 10 : Intégration ML dans backend

**Objectif** : Charger les modèles au démarrage du backend.

**Actions** :
1. Redémarrer le backend
2. Vérifier les logs : "Sports model loaded" / "Finance model loaded"
3. Tester `POST /api/v1/sports/predict` via Swagger
4. Tester `POST /api/v1/finance/predict`

**Validation** : Prédictions retournées avec modèle réel.

**Pourquoi** : Connecter le ML au backend pour des prédictions utilisables.

---

## Étape 11 : Interface de prédictions Sports

**Objectif** : Permettre aux utilisateurs de faire des prédictions sports.

**Actions** :
1. Aller sur /sports
2. Cliquer sur "Prédire" pour un match
3. Vérifier que la prédiction s'affiche
4. Vérifier en DB que la prédiction est sauvegardée

**Validation** : Prédiction affichée, enregistrée en base.

**Pourquoi** : Finaliser le flux utilisateur pour le module sports.

---

## Étape 12 : Interface de prédictions Finance

**Objectif** : Permettre aux utilisateurs de prédire les tendances boursières.

**Actions** :
1. Aller sur /finance
2. Rechercher une action (AAPL)
3. Cliquer sur "Générer une prédiction"
4. Vérifier l'affichage et la sauvegarde

**Validation** : Prédiction UP/DOWN affichée et sauvegardée.

**Pourquoi** : Compléter le module finance.

---

## Étape 13 : Historique des prédictions

**Objectif** : Afficher l'historique des prédictions utilisateur.

**Actions** :
1. Ajouter une page /history ou une section dans /dashboard
2. Récupérer les prédictions via `GET /api/v1/finance/predictions/history`
3. Afficher sous forme de tableau

**Validation** : Historique des prédictions visible.

**Pourquoi** : Permettre aux utilisateurs de suivre leurs prédictions passées.

---

## Étape 14 : Tests backend

**Objectif** : Écrire des tests unitaires pour les endpoints critiques.

**Actions** :
```bash
cd backend
# Créer tests/test_auth.py, tests/test_sports.py, tests/test_finance.py
pytest tests/
```

**Validation** : Tous les tests passent.

**Pourquoi** : Garantir la stabilité et la fiabilité du code.

---

## Étape 15 : Documentation et finalisation

**Objectif** : Compléter la documentation et préparer pour le déploiement.

**Actions** :
1. Vérifier que README.md est complet
2. Compléter docs/TECHNICAL.md
3. Créer un fichier DEPLOYMENT.md avec instructions de déploiement
4. Nettoyer le code, supprimer les console.log
5. Optimiser les performances (lazy loading, etc.)

**Validation** : Documentation claire, code propre.

**Pourquoi** : Faciliter la maintenance future et le déploiement.

---

## Étapes bonus (après MVP)

### Étape 16 : Intégration API externe Sports
- Remplacer les données mock par une vraie API (API-Sports)
- Gérer la pagination et le cache

### Étape 17 : Intégration API externe Finance
- Utiliser yfinance ou Alpha Vantage
- Implémenter des graphiques avec recharts

### Étape 18 : Amélioration des modèles ML
- Collecter plus de données réelles
- Feature engineering avancé
- Grid search pour hyperparamètres
- Évaluation croisée

### Étape 19 : Dashboard analytics
- Statistiques personnelles
- Taux de réussite des prédictions
- Graphiques de performance

### Étape 20 : Déploiement production
- Containerisation Docker
- CI/CD avec GitHub Actions
- Déploiement sur Heroku/AWS/DigitalOcean
- Configuration SSL

---

**Durée estimée du MVP** : 2-3 semaines en travaillant seul à temps partiel.

**Prochaine action** : Commencer par l'Étape 1.
