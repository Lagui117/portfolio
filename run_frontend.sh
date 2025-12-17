#!/bin/bash

echo "======================================"
echo "  Starting PredictWise Frontend"
echo "======================================"

# Navigate to frontend directory
cd "$(dirname "$0")/frontend" || exit

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        cat > .env << EOF
VITE_API_BASE_URL=http://localhost:5000/api/v1
VITE_APP_NAME=PredictWise
VITE_ENV=development
EOF
    fi
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start Vite dev server
echo ""
echo "======================================"
echo "  Frontend running on http://localhost:5173"
echo "  Connecting to backend at: $VITE_API_BASE_URL"
echo "======================================"
echo ""

npm run dev -- --host
