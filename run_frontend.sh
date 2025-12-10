#!/bin/bash

echo "======================================"
echo "  Starting PredictWise Frontend"
echo "======================================"

# Navigate to frontend directory
cd "$(dirname "$0")/frontend" || exit

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Creating from .env.example..."
    cp .env.example .env
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
echo "======================================"
echo ""

npm run dev
