#!/bin/bash

# PredictWise - Installation complete du projet

echo "================================================"
echo "  Installation de PredictWise"
echo "================================================"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Repertoire racine
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Verifier Python
echo -e "\n${BLUE}[1/7] Verification de Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}X Python 3 n'est pas installe${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}OK $PYTHON_VERSION${NC}"

# Verifier Node.js
echo -e "\n${BLUE}[2/7] Verification de Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}X Node.js n'est pas installe${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}OK Node.js $NODE_VERSION${NC}"

# Creer environnement virtuel
echo -e "\n${BLUE}[3/7] Creation de l'environnement virtuel...${NC}"
if [ ! -d "$ROOT_DIR/venv" ]; then
    python3 -m venv "$ROOT_DIR/venv"
    echo -e "${GREEN}OK Environnement virtuel cree${NC}"
else
    echo -e "${GREEN}OK Environnement virtuel existe deja${NC}"
fi
source "$ROOT_DIR/venv/bin/activate"

# Installer dependances backend
echo -e "\n${BLUE}[4/7] Installation des dependances backend...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -r "$ROOT_DIR/backend/requirements.txt"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}OK Dependances backend installees${NC}"
else
    echo -e "${RED}X Erreur lors de l'installation backend${NC}"
    exit 1
fi

# Installer dependances ML
echo -e "\n${BLUE}[5/7] Installation des dependances ML...${NC}"
pip install -r "$ROOT_DIR/ml/requirements.txt"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}OK Dependances ML installees${NC}"
else
    echo -e "${YELLOW}! Avertissement: erreur dependances ML${NC}"
fi

# Installer dependances frontend
echo -e "\n${BLUE}[6/7] Installation des dependances frontend...${NC}"
cd "$ROOT_DIR/frontend" || exit 1
npm install
if [ $? -eq 0 ]; then
    echo -e "${GREEN}OK Dependances frontend installees${NC}"
else
    echo -e "${RED}X Erreur lors de l'installation frontend${NC}"
    exit 1
fi
cd "$ROOT_DIR"

# Configurer fichiers .env
echo -e "\n${BLUE}[7/7] Configuration des fichiers d'environnement...${NC}"

if [ ! -f "$ROOT_DIR/backend/.env" ]; then
    if [ -f "$ROOT_DIR/backend/.env.example" ]; then
        cp "$ROOT_DIR/backend/.env.example" "$ROOT_DIR/backend/.env"
    fi
    echo -e "${GREEN}OK backend/.env cree${NC}"
else
    echo -e "${GREEN}OK backend/.env existe deja${NC}"
fi

if [ ! -f "$ROOT_DIR/frontend/.env" ]; then
    if [ -f "$ROOT_DIR/frontend/.env.example" ]; then
        cp "$ROOT_DIR/frontend/.env.example" "$ROOT_DIR/frontend/.env"
    fi
    echo -e "${GREEN}OK frontend/.env cree${NC}"
else
    echo -e "${GREEN}OK frontend/.env existe deja${NC}"
fi

# Initialiser la base de donnees
echo -e "\n${BLUE}Initialisation de la base de donnees...${NC}"
cd "$ROOT_DIR/backend"
python -c "from scripts.init_db import init_database; init_database()"
echo -e "${GREEN}OK Base de donnees initialisee${NC}"

# Peupler la base de donnees
echo -e "\n${BLUE}Peuplement de la base de donnees...${NC}"
python -c "from scripts.seed_db import seed_database; seed_database()"
echo -e "${GREEN}OK Donnees de demo ajoutees${NC}"
cd "$ROOT_DIR"

# Resume
echo -e "\n================================================"
echo -e "${GREEN}INSTALLATION TERMINEE !${NC}"
echo -e "================================================"
echo ""
echo "COMPTES DE TEST:"
echo "------------------------------------------------"
echo "  Admin: admin@predictwise.com / Admin123!"
echo "  Demo:  demo@predictwise.com / Demo123!"
echo "------------------------------------------------"
echo ""
echo "LANCEMENT:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    ./run_backend.sh"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    ./run_frontend.sh"
echo ""
echo "ACCES:"
echo "  Frontend: http://localhost:5173"
echo "  API:      http://localhost:5000/api/v1"
echo "  Health:   http://localhost:5000/health"
echo "================================================"
echo "   Swagger:  http://localhost:5000/api/docs"
echo ""
