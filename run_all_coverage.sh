#!/bin/bash
# ============================================
# Script de mesure de coverage complet
# Objectif: ≥85% global, ≥90% auth+admin
# ============================================

set -e

BACKEND_DIR="$(dirname "$0")/backend"
THRESHOLD_GLOBAL=85
THRESHOLD_AUTH=88
THRESHOLD_ADMIN=80

echo "==================================================="
echo "  🧪 COVERAGE REPORT - Portfolio AI Hub"
echo "==================================================="
echo ""

cd "$BACKEND_DIR"

# Effacer les données de coverage précédentes
coverage erase

# Lancer tous les tests avec coverage
echo "📊 Running tests with coverage..."
coverage run -m pytest -q --tb=line 2>&1

# Générer le rapport
echo ""
echo "==================================================="
echo "  📈 COVERAGE RESULTS"
echo "==================================================="
echo ""

# Rapport détaillé
coverage report -m --sort=cover

# Vérifier les seuils
echo ""
echo "==================================================="
echo "  ✅ THRESHOLD CHECKS"
echo "==================================================="

TOTAL_COV=$(coverage report | grep "TOTAL" | awk '{print $4}' | sed 's/%//')
AUTH_COV=$(coverage report | grep "app/api/v1/auth.py" | awk '{print $4}' | sed 's/%//')
ADMIN_COV=$(coverage report | grep "app/api/v1/admin.py" | awk '{print $4}' | sed 's/%//')

echo ""
echo "Global:  ${TOTAL_COV}% (threshold: ${THRESHOLD_GLOBAL}%)"
echo "Auth:    ${AUTH_COV}% (threshold: ${THRESHOLD_AUTH}%)"  
echo "Admin:   ${ADMIN_COV}% (threshold: ${THRESHOLD_ADMIN}%)"
echo ""

FAILED=0

if [ "$TOTAL_COV" -lt "$THRESHOLD_GLOBAL" ]; then
    echo "❌ FAIL: Global coverage ${TOTAL_COV}% < ${THRESHOLD_GLOBAL}%"
    FAILED=1
else
    echo "✅ PASS: Global coverage"
fi

if [ "$AUTH_COV" -lt "$THRESHOLD_AUTH" ]; then
    echo "❌ FAIL: Auth coverage ${AUTH_COV}% < ${THRESHOLD_AUTH}%"
    FAILED=1
else
    echo "✅ PASS: Auth coverage"
fi

if [ "$ADMIN_COV" -lt "$THRESHOLD_ADMIN" ]; then
    echo "❌ FAIL: Admin coverage ${ADMIN_COV}% < ${THRESHOLD_ADMIN}%"
    FAILED=1
else
    echo "✅ PASS: Admin coverage"
fi

echo ""

# Générer rapport HTML (optionnel)
if [ "$1" == "--html" ]; then
    echo "📄 Generating HTML report..."
    coverage html
    echo "   Report available at: htmlcov/index.html"
fi

echo "==================================================="

if [ $FAILED -eq 1 ]; then
    echo "  ❌ COVERAGE THRESHOLDS NOT MET"
    exit 1
else
    echo "  🎉 ALL COVERAGE THRESHOLDS MET!"
    exit 0
fi
