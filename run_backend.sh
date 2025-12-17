#!/bin/bash

echo "======================================"
echo "  Starting PredictWise Backend"
echo "======================================"

# Navigate to backend directory
cd "$(dirname "$0")/backend" || exit

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv ../venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source ../venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        cat > .env << EOF
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=predictwise-dev-secret-key-2024
JWT_SECRET_KEY=predictwise-jwt-secret-key-2024
DATABASE_URL=sqlite:///predictwise.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
USE_MOCK_SPORTS_API=true
USE_MOCK_FINANCE_API=true
EOF
    fi
fi

# Initialize database if it doesn't exist
if [ ! -f "predictwise.db" ]; then
    echo "Initializing database..."
    python -c "from scripts.init_db import init_database; init_database()"
    echo "Seeding database..."
    python -c "from scripts.seed_db import seed_database; seed_database()"
fi

# Start Flask server
echo ""
echo "======================================"
echo "  Backend running on http://localhost:5000"
echo "  Health check: http://localhost:5000/health"
echo "  API base: http://localhost:5000/api/v1"
echo "======================================"
echo "  Test accounts:"
echo "    Admin: admin@predictwise.com / Admin123!"
echo "    Demo:  demo@predictwise.com / Demo123!"
echo "======================================"
echo ""

export FLASK_APP=app.main:create_app
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
