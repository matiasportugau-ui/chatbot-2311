#!/bin/bash

# Function to kill processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $PYTHON_PID
    exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

# Start Python Backend
echo "Starting Python Backend..."
python3 sistema_completo_integrado.py &
PYTHON_PID=$!
echo "Backend PID: $PYTHON_PID"

# Wait a moment for backend to initialize
sleep 2

# Start Next.js Frontend
echo "Starting Next.js Frontend..."
npm run dev

# Wait for background process
wait $PYTHON_PID
