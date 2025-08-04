#!/bin/bash

# Filename: start.sh
# Location: the-nothing-app/gob01-mini/start.sh
# Purpose: Easy startup script for the Nothing App chat system

set -e  # Exit on any error

echo "🚀 Starting The Nothing App Chat System..."
echo "=========================================="

# Check if conda environment exists
if ! conda env list | grep -q "agentic-framework"; then
    echo "❌ Conda environment 'agentic-framework' not found!"
    echo "Creating environment from environment.yml..."
    conda env create -f environment.yml
    echo "✅ Environment created successfully!"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create a .env file with your OPENROUTER_API_KEY"
    echo "Example:"
    echo "OPENROUTER_API_KEY=your_api_key_here"
    exit 1
fi

# Check if API key is set
if grep -q "your_openrouter_api_key_here" .env || ! grep -q "OPENROUTER_API_KEY=" .env; then
    echo "❌ Please set your OPENROUTER_API_KEY in the .env file"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed!"
fi

echo "🔧 Starting backend server..."
# Start backend in background using conda environment
/home/ds/miniconda3/envs/agentic-framework/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

echo "🎨 Starting frontend server..."
# Start frontend in background
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Both servers are starting up!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ Servers stopped. Goodbye!"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
