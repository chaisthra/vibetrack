#!/bin/bash

echo "🚀 Starting VibeTrack in production mode..."

# Function to cleanup background processes on exit
cleanup() {
    echo "
🛑 Shutting down VibeTrack..."
    kill $(jobs -p)
    exit
}

# Set up cleanup trap
trap cleanup EXIT

# Start backend server in production mode
echo "📡 Starting backend server..."
cd backend
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4 &

# Wait a bit for backend to initialize
sleep 3

# Start frontend in production mode
echo "🌐 Starting frontend..."
cd ../frontend
streamlit run app.py --server.address 0.0.0.0 --server.port ${STREAMLIT_PORT:-8501} --server.headless true &

# Keep script running and show logs
echo "
✨ VibeTrack is running in production mode!
- Frontend: http://0.0.0.0:${STREAMLIT_PORT:-8501}
- Backend: http://0.0.0.0:${PORT:-8000}

Press Ctrl+C to stop all servers.
"

# Wait for all background processes
wait 