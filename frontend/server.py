#!/usr/bin/env python3
"""
Simple HTTP server for MultiLLM Frontend
Serves the static frontend files on port 8080
"""

import http.server
import socketserver
import os
import sys

PORT = 1000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to set proper MIME types and CORS headers"""
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # Set proper MIME types
        if self.path.endswith('.js'):
            self.send_header('Content-Type', 'application/javascript')
        elif self.path.endswith('.css'):
            self.send_header('Content-Type', 'text/css')
        elif self.path.endswith('.html'):
            self.send_header('Content-Type', 'text/html')
        super().end_headers()

def main():
    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 Frontend server running at http://localhost:{PORT}/")
        print(f"📁 Serving directory: {os.getcwd()}")
        print(f"\n💡 Open http://localhost:{PORT} in your browser")
        print(f"🛑 Press Ctrl+C to stop the server\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped. Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    main()
