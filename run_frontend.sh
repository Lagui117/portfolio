#!/bin/bash

echo "======================================"
echo "  Starting PredictWise Frontend"
echo "======================================"

# Navigate to frontend directory
cd "$(dirname "$0")/frontend" || exit

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Creating default .env..."
    cat > .env << EOF
VITE_API_BASE_URL=http://localhost:5000/api/v1
EOF
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
