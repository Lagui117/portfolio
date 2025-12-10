# Changelog - PredictWise

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/).

---

## [1.0.0] - 2025-12-09

### ✨ Ajouté

#### Infrastructure
- Script d'installation automatique `install.sh`
- Fichier `.gitignore` complet (Python, Node, ML, OS)
- Fichier `QUICKSTART.md` pour démarrage rapide
- Fichier `HEALTH_CHECK.md` pour état de santé du projet
- Fichier `CHANGELOG.md` pour traçabilité des versions

#### Documentation
- Section "Installation" enrichie dans README.md
- Section "Configuration" avec exemples `.env`
- Section "Tests" avec commandes
- Section "Structure du projet" avec arborescence
- Section "Déploiement" avec recommendations
- Section "Contribution" et "Licence"

#### Machine Learning
- Script `ml/scripts/evaluate_models.py` (450 lignes)
  - Métriques complètes : accuracy, precision, recall, F1-score
  - Matrices de confusion
  - Classification reports détaillés
  - Feature importance pour les deux modèles
  - Exemples de prédictions avec probabilités
  
- Service centralisé `backend/app/services/prediction_service.py` (384 lignes)
  - Classe PredictionService singleton
  - Méthodes predict_sport_event() et predict_stock_movement()
  - Fallback strategies si modèles non disponibles
  - Logging détaillé
  - Méthode get_models_info() pour diagnostic

- Documentation `docs/ML_OVERVIEW.md` (400+ lignes)
  - Description complète des algorithmes
  - Liste exhaustive des features (13 sports, 14 finance)
  - Métriques de performance
  - Exemples d'utilisation du service
  - Guide de feature engineering
  - Améliorations futures suggérées
  - Disclaimer éducatif

- Documentation `ml/README.md` améliorée (250+ lignes)
  - Structure professionnelle
  - Tableaux récapitulatifs des modèles
  - Workflow ML complet
  - Guide de développement
  - Conseils et bonnes pratiques

- Documentation `docs/AMELIORATIONS_ML.md`
  - Récapitulatif des améliorations ML
  - Tests effectués et résultats
  - Points forts et crédibilité renforcée

#### Frontend
- Note sur `npm install` dans README

### 🔧 Corrigé

- Date incorrecte dans README.md (2025 → 2024)
- Suppression de `ml/data/.gitkeep` redondant
- Scripts rendus exécutables (`chmod +x`)
- Organisation des .gitkeep (raw/ et processed/ conservés)

### 📝 Modifié

- README.md restructuré et enrichi
  - Section "Démarrage Rapide" réorganisée
  - Ajout de sections Configuration, Tests, Structure
  - Meilleure présentation du ML
  - Footer avec contribution et licence

### 🗑️ Supprimé

- Fichier `ml/data/.gitkeep` (redondant avec raw/ et processed/)

---

## [0.9.0] - 2025-12-08

### ✨ Développement complet du projet

#### Backend
- API REST Flask 3.0 avec 13 endpoints
- Authentification JWT avec bcrypt
- 8 modèles SQLAlchemy (User, Prediction, Consultation, SportEvent, etc.)
- Swagger UI intégré (`/api/docs`)
- Services métier (sports_service.py, finance_service.py)
- Tests unitaires avec pytest

#### Frontend
- Application React 18 + Vite
- 4 pages complètes (Login, Dashboard, Sports, Finance)
- Auth Context avec protection des routes
- API Client avec interceptors automatiques
- Interface Tailwind CSS responsive

#### Machine Learning
- Modèle Sports : RandomForestClassifier (13 features, 45% accuracy)
- Modèle Finance : LogisticRegression + Scaler (14 features, 59% accuracy)
- Scripts d'entraînement avec données synthétiques
- Scripts `train_sports_model.py` et `train_finance_model.py`

#### Documentation initiale
- `docs/API_SPEC.md` - Spécification des 13 endpoints
- `docs/API_GUIDE.md` - Guide d'utilisation
- `docs/TECHNICAL.md` - Documentation technique
- `docs/DEVELOPMENT_PLAN.md` - Plan de développement
- `DEVELOPPEMENT_COMPLET.md` - Récapitulatif de développement
- `PROJET_TERMINE.md` - Projet terminé

---

## Format des Versions

### Types de changements

- **Ajouté** : Nouvelles fonctionnalités
- **Modifié** : Changements dans les fonctionnalités existantes
- **Déprécié** : Fonctionnalités qui seront supprimées
- **Supprimé** : Fonctionnalités supprimées
- **Corrigé** : Corrections de bugs
- **Sécurité** : Corrections de vulnérabilités

### Numérotation des versions

`MAJEUR.MINEUR.PATCH`

- **MAJEUR** : Changements incompatibles avec les versions précédentes
- **MINEUR** : Ajout de fonctionnalités rétrocompatibles
- **PATCH** : Corrections de bugs rétrocompatibles

---

**Mainteneur:** GitHub Copilot  
**Dernière mise à jour:** 2025-12-09
