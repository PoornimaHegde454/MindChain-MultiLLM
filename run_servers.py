#!/usr/bin/env python3
"""
Run both backend and frontend servers in separate threads
"""

import threading
import sys
import os
import signal
import uvicorn
from app.config import settings

# Import frontend server
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'frontend'))
from server import MyHTTPRequestHandler
import socketserver

# Global flag for graceful shutdown
shutdown_flag = threading.Event()

def run_backend():
    """Run the FastAPI backend server"""
    print("🚀 Starting backend server on http://localhost:8000")
    print("📊 API docs available at http://localhost:8000/docs")
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload when running in thread
            log_level=settings.LOG_LEVEL.lower()
        )
    except Exception as e:
        print(f"❌ Backend server error: {e}")
        shutdown_flag.set()

def run_frontend():
    """Run the frontend HTTP server"""
    PORT = 1000
    # Change to frontend directory
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    original_dir = os.getcwd()
    os.chdir(frontend_dir)
    
    print(f"🌐 Starting frontend server on http://localhost:{PORT}")
    print(f"📁 Serving directory: {os.getcwd()}")
    print(f"💡 Open http://localhost:{PORT} in your browser")
    
    try:
        httpd = socketserver.TCPServer(("", PORT), MyHTTPRequestHandler)
        httpd.timeout = 1
        
        # Run server in a way that respects shutdown flag
        while not shutdown_flag.is_set():
            httpd.handle_request()
        
        httpd.shutdown()
        httpd.server_close()
    except Exception as e:
        if not shutdown_flag.is_set():
            print(f"❌ Frontend server error: {e}")
        shutdown_flag.set()
    finally:
        os.chdir(original_dir)

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n🛑 Shutting down servers...")
    shutdown_flag.set()
    sys.exit(0)

def main():
    """Main function to start both servers in threads"""
    print("=" * 60)
    print("🚀 Starting MultiLLM Router Servers")
    print("=" * 60)
    print(f"📊 Backend: http://localhost:8000")
    print(f"🌐 Frontend: http://localhost:1000")
    print(f"\n🛑 Press Ctrl+C to stop both servers\n")
    
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create threads for both servers
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    
    # Start both threads
    backend_thread.start()
    frontend_thread.start()
    
    print("✅ Both servers started!")
    
    # Wait for both threads (they will run until interrupted)
    try:
        backend_thread.join()
        frontend_thread.join()
    except KeyboardInterrupt:
        print("\n\n👋 Servers stopped. Goodbye!")
        shutdown_flag.set()
        sys.exit(0)

if __name__ == "__main__":
    main()

