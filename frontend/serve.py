#!/usr/bin/env python3
"""
Simple Python HTTP server for serving React SPA with client-side routing.
Serves static files and handles SPA routing by serving index.html for all non-file routes.
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 8080
DIRECTORY = "/home/site/wwwroot"

class SPAHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler that serves index.html for SPA routing"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        """Handle GET requests with SPA routing support"""
        # Get the requested path
        path = self.translate_path(self.path)
        
        # If path is a directory, serve index.html
        if os.path.isdir(path):
            index_path = os.path.join(path, 'index.html')
            if os.path.exists(index_path):
                self.path = '/index.html'
        # If file doesn't exist and it's not a file with extension, serve index.html for SPA routing
        elif not os.path.exists(path) and '.' not in os.path.basename(self.path):
            self.path = '/index.html'
        
        return super().do_GET()
    
    def end_headers(self):
        """Add CORS and caching headers"""
        # Disable caching for HTML files
        if self.path.endswith('.html'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()

def main():
    """Start the HTTP server"""
    print(f"Starting Python HTTP server on port {PORT}...")
    print(f"Serving files from: {DIRECTORY}")
    
    # Change to the directory to serve
    os.chdir(DIRECTORY)
    
    # Verify index.html exists
    if not os.path.exists('index.html'):
        print(f"WARNING: index.html not found in {DIRECTORY}")
        print(f"Directory contents: {os.listdir(DIRECTORY)}")
    
    with socketserver.TCPServer(("", PORT), SPAHTTPRequestHandler) as httpd:
        print(f"Server running at http://0.0.0.0:{PORT}/")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
