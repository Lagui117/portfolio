# Guide d'Exécution des Tests - PredictWise

Ce document explique comment exécuter la suite complète de tests pour le projet PredictWise.

## Installation des Dépendances

### Backend

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### ML

```bash
cd ml
pip install -r requirements.txt
pip install pytest pytest-cov numpy pandas scikit-learn joblib
```

### Frontend

```bash
cd frontend
npm install
npm install --save-dev vitest @vitest/ui @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

## Exécution des Tests

### Backend Tests (pytest)

```bash
cd backend

# Exécuter tous les tests
pytest

# Avec couverture
pytest --cov=app --cov-report=term-missing

# Génération rapport HTML
pytest --cov=app --cov-report=html
# Ouvrir htmlcov/index.html dans un navigateur

# Tests spécifiques
pytest tests/test_auth_endpoints.py
pytest tests/test_sports_endpoints.py -v
pytest tests/test_prediction_service.py::TestPredictionService::test_predict_sport_with_model
```

### ML Tests (pytest)

```bash
cd ml

# Exécuter tous les tests ML
pytest tests/

# Avec couverture
pytest tests/ --cov=scripts --cov-report=term-missing

# Tests spécifiques
pytest tests/test_train_sports_model.py -v
pytest tests/test_prediction_integration.py
```

### Frontend Tests (Vitest)

```bash
cd frontend

# Exécuter tous les tests
npm run test

# Mode watch (développement)
npm run test:watch

# Avec UI interactive
npm run test:ui

# Avec couverture
npm run test:coverage

# Tests spécifiques
npx vitest src/tests/LoginPage.test.jsx
npx vitest src/tests/services/
```

## Commandes Globales

### Exécuter TOUS les tests (backend + ML + frontend)

Créer un script `run_all_tests.sh` à la racine :

```bash
#!/bin/bash

echo "========================================="
echo "BACKEND TESTS"
echo "========================================="
cd backend
pytest --cov=app --cov-report=term-missing
BACKEND_EXIT=$?

echo ""
echo "========================================="
echo "ML TESTS"
echo "========================================="
cd ../ml
pytest tests/ --cov=scripts --cov-report=term-missing
ML_EXIT=$?

echo ""
echo "========================================="
echo "FRONTEND TESTS"
echo "========================================="
cd ../frontend
npm run test -- --run
FRONTEND_EXIT=$?

echo ""
echo "========================================="
echo "RÉSUMÉ"
echo "========================================="
echo "Backend: $([ $BACKEND_EXIT -eq 0 ] && echo '✓ PASS' || echo '✗ FAIL')"
echo "ML: $([ $ML_EXIT -eq 0 ] && echo '✓ PASS' || echo '✗ FAIL')"
echo "Frontend: $([ $FRONTEND_EXIT -eq 0 ] && echo '✓ PASS' || echo '✗ FAIL')"

exit $(( $BACKEND_EXIT + $ML_EXIT + $FRONTEND_EXIT ))
```

Puis exécuter :

```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

## Couverture de Tests Attendue

### Backend
- Objectif: 90-95%
- Fichiers critiques:
  - app/api/v1/auth.py: 100%
  - app/api/v1/sports.py: 95%
  - app/api/v1/finance.py: 95%
  - app/services/prediction_service.py: 90%
  - app/services/gpt_service.py: 85%
  - app/models/user.py: 100%

### ML
- Objectif: 85-90%
- Fichiers critiques:
  - scripts/train_sports_model.py: 90%
  - scripts/train_finance_model.py: 90%
  - Backend integration: 85%

### Frontend
- Objectif: 80-85%
- Fichiers critiques:
  - routes/SignupPage.jsx: 85%
  - routes/LoginPage.jsx: 85%
  - services/authService.js: 95%
  - services/sportsService.js: 90%
  - services/financeService.js: 90%

## Scripts package.json (Frontend)

Ajouter ces scripts à `frontend/package.json` :

```json
{
  "scripts": {
    "test": "vitest",
    "test:watch": "vitest --watch",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:run": "vitest run"
  }
}
```

## Troubleshooting

### Backend

**Erreur: ImportError**
```bash
# S'assurer que PYTHONPATH inclut backend/
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
pytest
```

**Erreur: Database locked**
```bash
# Supprimer la base de test
rm -f backend/test.db
pytest
```

### ML

**Erreur: Module not found**
```bash
# Installer les dépendances
pip install numpy pandas scikit-learn joblib
```

### Frontend

**Erreur: Cannot find module**
```bash
# Réinstaller les dépendances
rm -rf node_modules package-lock.json
npm install
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom jsdom
```

**Erreur: ReferenceError: localStorage is not defined**
- Vérifier que `src/setupTests.js` est bien présent et configuré dans `vitest.config.js`

## Intégration Continue (CI/CD)

Exemple de workflow GitHub Actions (`.github/workflows/tests.yml`) :

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          cd backend
          pip install -r requirements.txt -r requirements-test.txt
          pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3

  ml:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          cd ml
          pip install -r requirements.txt pytest pytest-cov
          pytest tests/ --cov=scripts

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: |
          cd frontend
          npm ci
          npm run test:coverage
```

## Métriques de Qualité

Après chaque exécution, vérifier :

1. Taux de couverture global ≥ 85%
2. Tous les tests passent (0 échecs)
3. Aucun warning critique
4. Temps d'exécution < 2 minutes (backend+ML+frontend)

## Contacts

Pour toute question sur les tests :
- Backend/ML: Vérifier les fixtures dans `conftest.py`
- Frontend: Vérifier les mocks dans `setupTests.js`
