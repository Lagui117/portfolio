#!/bin/bash

echo "======================================"
echo "  Starting PredictWise Backend"
echo "======================================"

# Navigate to backend directory
cd "$(dirname "$0")/backend" || exit

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Creating default .env..."
    cat > .env << EOF
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key-change-in-production
DATABASE_URL=sqlite:///predictwise.db
CORS_ORIGINS=http://localhost:5173
EOF
fi

# Start Flask server
echo ""
echo "======================================"
echo "  Backend running on http://localhost:5000"
echo "  API documentation: http://localhost:5000/api/docs"
echo "======================================"
echo ""

export FLASK_APP=app/main.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
