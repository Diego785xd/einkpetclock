#!/usr/bin/env python3
"""
API Server Wrapper - automatically uses FastAPI or simple HTTP server
"""
import sys

# Try to use FastAPI first
try:
    import fastapi
    import uvicorn
    HAS_FASTAPI = True
    print("Using FastAPI")
except ImportError:
    HAS_FASTAPI = False
    print("FastAPI not available, using simple HTTP server")

if HAS_FASTAPI:
    # Use the full FastAPI implementation
    from web.api import app
    
    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=5000)
else:
    # Use simple HTTP server
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from core.config import Config
    from core.state import get_pet_state, get_message_log
    
    class SimpleAPIHandler(BaseHTTPRequestHandler):
        """Simple HTTP handler for basic API functionality"""
        
        def log_message(self, format, *args):
            """Custom log format"""
            sys.stderr.write(f"[API] {format%args}\n")
        
        def send_json(self, code, data):
            """Send JSON response"""
            self.send_response(code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        
        def do_POST(self):
            """Handle POST requests"""
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            
            try:
                if self.path == '/api/message':
                    data = json.loads(body) if body != '{}' else {}
                    message_text = data.get('message', data.get('text', ''))
                    from_device = data.get('from_device', data.get('from', 'unknown'))
                    
                    if not message_text:
                        self.send_json(400, {'error': 'message text required'})
                        return
                    
                    # Write to message log
                    message_log = get_message_log()
                    message_log.add_message(message_text, from_device)
                    
                    # Set flag for display manager
                    Path('/tmp/eink_flags/new_message').write_text(json.dumps({
                        'text': message_text,
                        'from': from_device
                    }))
                    
                    self.send_json(200, {'status': 'ok', 'message': 'received'})
                
                elif self.path == '/api/poke':
                    # Set poke flag
                    Path('/tmp/eink_flags/poke').touch()
                    self.send_json(200, {'status': 'ok', 'action': 'poked'})
                
                elif self.path == '/api/feed':
                    # Set feed flag
                    Path('/tmp/eink_flags/feed').touch()
                    
                    # Update pet state
                    pet = get_pet_state()
                    pet.feed()
                    
                    self.send_json(200, {'status': 'ok', 'action': 'fed'})
                
                else:
                    self.send_json(404, {'error': 'not found'})
            
            except Exception as e:
                self.send_json(500, {'error': str(e)})
        
        def do_GET(self):
            """Handle GET requests"""
            try:
                if self.path == '/api/status' or self.path == '/':
                    pet = get_pet_state()
                    message_log = get_message_log()
                    config = Config()
                    
                    pet_data = pet.data
                    status = {
                        'device_name': config.DEVICE_NAME,
                        'pet_name': pet_data.get('name', 'Unknown'),
                        'hunger': pet_data.get('hunger', 50),
                        'happiness': pet_data.get('happiness', 50),
                        'health': pet_data.get('health', 100),
                        'messages_count': len(message_log.get_recent(10)),
                        'online': True,
                        'mode': 'simple_http'
                    }
                    
                    self.send_json(200, status)
                
                else:
                    self.send_json(404, {'error': 'not found'})
            
            except Exception as e:
                self.send_json(500, {'error': str(e)})
    
    if __name__ == "__main__":
        # Ensure flag directory exists
        Path('/tmp/eink_flags').mkdir(parents=True, exist_ok=True)
        
        server = HTTPServer(('0.0.0.0', 5000), SimpleAPIHandler)
        print("Simple HTTP API server running on http://0.0.0.0:5000")
        print("Endpoints:")
        print("  GET  /api/status - Get device status")
        print("  POST /api/message - Send message (JSON: {'message': 'text', 'from_device': 'name'})")
        print("  POST /api/poke - Poke the pet")
        print("  POST /api/feed - Feed the pet")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            server.shutdown()
