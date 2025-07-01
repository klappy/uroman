"""
Vercel serverless function for uroman romanization
Place this in api/romanize.py in your Vercel project
"""

from http.server import BaseHTTPRequestHandler
import json
import uroman as ur

# Initialize uroman instance for reuse
uroman_instance = None

def get_uroman():
    """Get or create uroman instance"""
    global uroman_instance
    if uroman_instance is None:
        uroman_instance = ur.Uroman()
    return uroman_instance

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters
            text = body.get('text', '')
            language = body.get('language', None)
            format_str = body.get('format', 'str')
            
            # Map format string to RomFormat enum
            format_map = {
                'str': ur.RomFormat.STR,
                'edges': ur.RomFormat.EDGES,
                'alts': ur.RomFormat.ALTS,
                'lattice': ur.RomFormat.LATTICE
            }
            rom_format = format_map.get(format_str, ur.RomFormat.STR)
            
            # Get uroman instance
            uroman = get_uroman()
            
            # Romanize
            result = uroman.romanize_string(text, lcode=language, rom_format=rom_format)
            
            # Format response
            if isinstance(result, str):
                response_data = {
                    'original': text,
                    'romanized': result,
                    'format': format_str
                }
            else:
                response_data = {
                    'original': text,
                    'romanized': [json.loads(edge.json()) for edge in result],
                    'format': format_str
                }
            
            if language:
                response_data['language'] = language
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {
                'error': str(e),
                'message': 'Failed to romanize text'
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
