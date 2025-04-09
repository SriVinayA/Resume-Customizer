#!/usr/bin/env python3
"""
Simple HTTP Server for Frontend 

This script starts a simple HTTP server to serve the frontend files.
It will serve the current directory on port 3000.

Usage:
    python serve.py
"""

import http.server
import socketserver
import os
import webbrowser
from urllib.parse import urlparse

# Configuration
PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def log_message(self, format, *args):
        # Check if we're logging a successful GET request
        if len(args) >= 2 and isinstance(args[0], str) and args[0].startswith('GET ') and args[1] == '200':
            print(f"Serving: {args[0].split()[1]}")
        else:
            # Fall back to default logging for other cases
            super().log_message(format, *args)

def run_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Server started at http://localhost:{PORT}")
        print(f"Serving directory: {DIRECTORY}")
        print("Press Ctrl+C to stop the server")
        
        # Open browser automatically
        webbrowser.open(f"http://localhost:{PORT}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    run_server() 