#!/bin/bash

# Kavalar Local Launch Script (Unix/macOS/Git Bash)
echo "=================================================="
echo "Starting Kavalar Local Setup & Launch"
echo "=================================================="

# Check Python
if ! command -v python &> /dev/null; then
    echo "ERROR: python is not installed or not in PATH."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH."
    exit 1
fi

# Set up Backend Virtual Environment
echo "Setting up Python virtual environment in backend..."
cd backend
if [ ! -d "venv" ]; then
    python -m venv venv
fi

source venv/bin/activate
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Create default .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating default backend .env file..."
    echo "DATABASE_URL=sqlite:///./kavalar.db" > .env
    echo "MODEL_NAME=llama-3.3-70b-versatile" >> .env
    echo "GROQ_API_KEY=your_groq_api_key_here" >> .env
fi

# Train the Anomaly Detector Baseline
echo "Training baseline profile..."
python train_baseline.py

# Start Backend Server
echo "Launching FastAPI backend..."
uvicorn main:app --port 8000 --reload &
BACKEND_PID=$!

cd ..

# Set up Frontend
echo "Installing frontend dependencies..."
cd frontend
npm install

# Start Frontend
echo "Launching Next.js frontend on http://localhost:3000..."
npm run dev &
FRONTEND_PID=$!

echo "=================================================="
echo "Kavalar is now starting up!"
echo "Backend:  http://localhost:8000 (Swagger docs at /docs)"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop both servers."
echo "=================================================="

# Handle termination of both processes
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

trap cleanup INT TERM

# Wait for background jobs to finish
wait
