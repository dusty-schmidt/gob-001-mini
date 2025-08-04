#!/usr/bin/env python3

"""
Filename: start.py
Location: the-nothing-app/gob01-mini/start.py
Purpose: Easy Python startup script for the Nothing App chat system
"""

import os
import sys
import subprocess
import signal
import time
import threading
from pathlib import Path

def print_banner():
    print("🚀 Starting The Nothing App Chat System...")
    print("==========================================")

def check_conda_env():
    """Check if the conda environment exists"""
    try:
        result = subprocess.run(['conda', 'env', 'list'], capture_output=True, text=True)
        if 'agentic-framework' not in result.stdout:
            print("❌ Conda environment 'agentic-framework' not found!")
            print("Creating environment from environment.yml...")
            subprocess.run(['conda', 'env', 'create', '-f', 'environment.yml'], check=True)
            print("✅ Environment created successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error with conda. Make sure conda is installed and available.")
        return False
    except FileNotFoundError:
        print("❌ Conda not found. Please install conda first.")
        return False

def check_env_file():
    """Check if .env file exists and has API key"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your OPENROUTER_API_KEY")
        print("Example:")
        print("OPENROUTER_API_KEY=your_api_key_here")
        return False
    
    content = env_file.read_text()
    if 'your_openrouter_api_key_here' in content or 'OPENROUTER_API_KEY=' not in content:
        print("❌ Please set your OPENROUTER_API_KEY in the .env file")
        return False
    
    return True

def check_frontend_deps():
    """Check if frontend dependencies are installed"""
    node_modules = Path('frontend/node_modules')
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        subprocess.run(['npm', 'install'], cwd='frontend', check=True)
        print("✅ Frontend dependencies installed!")

def start_backend():
    """Start the backend server"""
    print("🔧 Starting backend server...")
    conda_python = '/home/ds/miniconda3/envs/agentic-framework/bin/python'
    cmd = [conda_python, '-m', 'uvicorn', 'backend.main:app', '--host', '0.0.0.0', '--port', '8001', '--reload']
    return subprocess.Popen(cmd)

def start_frontend():
    """Start the frontend server"""
    print("🎨 Starting frontend server...")
    return subprocess.Popen(['npm', 'run', 'dev'], cwd='frontend')

def main():
    print_banner()
    
    # Check prerequisites
    if not check_conda_env():
        sys.exit(1)
    
    if not check_env_file():
        sys.exit(1)
    
    check_frontend_deps()
    
    # Start servers
    backend_process = start_backend()
    time.sleep(3)  # Wait for backend to start
    
    frontend_process = start_frontend()
    
    print()
    print("✅ Both servers are starting up!")
    print("📱 Frontend: http://localhost:5173")
    print("🔧 Backend API: http://localhost:8001")
    print("📚 API Docs: http://localhost:8001/docs")
    print()
    print("Press Ctrl+C to stop both servers")
    
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait a bit for graceful shutdown
        time.sleep(2)
        
        # Force kill if still running
        try:
            backend_process.kill()
            frontend_process.kill()
        except:
            pass
        
        print("✅ Servers stopped. Goodbye!")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Wait for processes
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
