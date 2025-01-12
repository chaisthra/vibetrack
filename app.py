import os
import sys
import subprocess
import threading
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def start_backend():
    """Start the FastAPI backend server"""
    try:
        # Change to backend directory
        os.chdir(str(project_root / 'backend'))
        # Start the backend server
        subprocess.Popen([
            'uvicorn', 
            'main:app', 
            '--host', '0.0.0.0',
            '--port', str(os.getenv('PORT', 8000))
        ])
    except Exception as e:
        print(f"Error starting backend: {e}")

# Start backend in a separate thread
backend_thread = threading.Thread(target=start_backend, daemon=True)
backend_thread.start()

# Import and run the Streamlit frontend
from frontend.app import *

if __name__ == "__main__":
    # The Streamlit app will run automatically when this file is executed by Streamlit
    pass 