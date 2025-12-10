#!/bin/bash

# PredictWise - Installation complète du projet

echo "================================================"
echo "  Installation de PredictWise"
echo "================================================"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier Python
echo -e "\n${BLUE}[1/5] Vérification de Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"

# Vérifier Node.js
echo -e "\n${BLUE}[2/5] Vérification de Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js n'est pas installé${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js $NODE_VERSION${NC}"

# Installer dépendances backend
echo -e "\n${BLUE}[3/5] Installation des dépendances backend...${NC}"
cd backend || exit 1
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Environnement virtuel créé${NC}"
fi
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dépendances backend installées${NC}"
else
    echo -e "${RED}❌ Erreur lors de l'installation backend${NC}"
    exit 1
fi
cd ..

# Installer dépendances frontend
echo -e "\n${BLUE}[4/5] Installation des dépendances frontend...${NC}"
cd frontend || exit 1
npm install
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dépendances frontend installées${NC}"
else
    echo -e "${RED}❌ Erreur lors de l'installation frontend${NC}"
    exit 1
fi
cd ..

# Créer fichiers .env si manquants
echo -e "\n${BLUE}[5/5] Configuration des fichiers d'environnement...${NC}"

if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env 2>/dev/null || true
    echo -e "${GREEN}✓ backend/.env créé${NC}"
else
    echo -e "${GREEN}✓ backend/.env existe déjà${NC}"
fi

if [ ! -f "frontend/.env" ]; then
    cp frontend/.env.example frontend/.env 2>/dev/null || true
    echo -e "${GREEN}✓ frontend/.env créé${NC}"
else
    echo -e "${GREEN}✓ frontend/.env existe déjà${NC}"
fi

# Résumé
echo -e "\n================================================"
echo -e "${GREEN}✅ Installation terminée !${NC}"
echo -e "================================================"
echo ""
echo "Prochaines étapes :"
echo ""
echo "1. Entraîner les modèles ML :"
echo "   cd ml/scripts"
echo "   python train_sports_model.py"
echo "   python train_finance_model.py"
echo ""
echo "2. Lancer le backend :"
echo "   ./run_backend.sh"
echo ""
echo "3. Lancer le frontend (dans un autre terminal) :"
echo "   ./run_frontend.sh"
echo ""
echo "4. Accéder à l'application :"
echo "   Frontend: http://localhost:5173"
echo "   API:      http://localhost:5000/api/v1"
echo "   Swagger:  http://localhost:5000/api/docs"
echo ""
