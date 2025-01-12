#!/bin/bash

echo "🚀 Starting VibeTrack..."

# Function to cleanup background processes on exit
cleanup() {
    echo "
🛑 Shutting down VibeTrack..."
    kill $(jobs -p)
    exit
}

# Set up cleanup trap
trap cleanup EXIT

# Start backend server
echo "📡 Starting backend server..."
cd backend
uvicorn main:app --reload &

# Wait a bit for backend to initialize
sleep 3

# Start frontend
echo "🌐 Starting frontend..."
cd ../frontend
streamlit run app.py &

# Keep script running and show logs
echo "
✨ VibeTrack is running!
- Frontend: http://localhost:8501
- Backend: http://localhost:8000

Press Ctrl+C to stop all servers.
"

# Wait for all background processes
wait 