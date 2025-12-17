#!/bin/bash

# Script pour executer TOUS les tests du projet PredictWise
# Backend (pytest) + ML (pytest) + Frontend (vitest)

set -e  # Arreter si erreur

echo "=================================================="
echo "🧪 SUITE DE TESTS COMPLÈTE - PredictWise"
echo "=================================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BACKEND_EXIT=0
ML_EXIT=0
FRONTEND_EXIT=0

# BACKEND TESTS
echo "=================================================="
echo "📦 BACKEND TESTS (pytest)"
echo "=================================================="
cd backend
if pytest --cov=app --cov-report=term-missing; then
    echo -e "${GREEN}✓ Backend tests PASS${NC}"
else
    echo -e "${RED}✗ Backend tests FAIL${NC}"
    BACKEND_EXIT=1
fi
cd ..
echo ""

# ML TESTS
echo "=================================================="
echo "🤖 ML TESTS (pytest)"
echo "=================================================="
cd ml
if pytest tests/ --cov=scripts --cov-report=term-missing; then
    echo -e "${GREEN}✓ ML tests PASS${NC}"
else
    echo -e "${RED}✗ ML tests FAIL${NC}"
    ML_EXIT=1
fi
cd ..
echo ""

# FRONTEND TESTS
echo "=================================================="
echo "🖥️  FRONTEND TESTS (vitest)"
echo "=================================================="
cd frontend
if npm run test:run 2>/dev/null || npx vitest run; then
    echo -e "${GREEN}✓ Frontend tests PASS${NC}"
else
    echo -e "${RED}✗ Frontend tests FAIL${NC}"
    FRONTEND_EXIT=1
fi
cd ..
echo ""

# RÉSUMÉ
echo "=================================================="
echo "📊 RÉSUMÉ"
echo "=================================================="
if [ $BACKEND_EXIT -eq 0 ]; then
    echo -e "Backend:  ${GREEN}✓ PASS${NC}"
else
    echo -e "Backend:  ${RED}✗ FAIL${NC}"
fi

if [ $ML_EXIT -eq 0 ]; then
    echo -e "ML:       ${GREEN}✓ PASS${NC}"
else
    echo -e "ML:       ${RED}✗ FAIL${NC}"
fi

if [ $FRONTEND_EXIT -eq 0 ]; then
    echo -e "Frontend: ${GREEN}✓ PASS${NC}"
else
    echo -e "Frontend: ${RED}✗ FAIL${NC}"
fi

TOTAL_EXIT=$(( BACKEND_EXIT + ML_EXIT + FRONTEND_EXIT ))

echo ""
if [ $TOTAL_EXIT -eq 0 ]; then
    echo -e "${GREEN}=================================================="
    echo "✓ TOUS LES TESTS PASSENT!"
    echo "==================================================${NC}"
    exit 0
else
    echo -e "${RED}=================================================="
    echo "✗ CERTAINS TESTS ONT ÉCHOUÉ"
    echo "==================================================${NC}"
    exit 1
fi
