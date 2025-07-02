"""
Uroman MCP (Model Context Protocol) Server on Modal
This allows AI assistants to use uroman for text romanization
"""

import modal
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Create our Modal app
app = modal.App("uroman-mcp-server")

# Define the container image
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "regex",
        "unicodedata2",
        "fastapi[standard]",
    )
    .add_local_dir("../uroman", "/app/uroman")
)

# Global uroman instance
uroman_instance = None

def get_uroman():
    """Get or create uroman instance"""
    global uroman_instance
    if uroman_instance is None:
        sys.path.insert(0, '/app')
        from uroman.uroman import Uroman
        uroman_instance = Uroman()
        print("Uroman initialized for MCP!")
    return uroman_instance

@app.function(image=image, scaledown_window=300)
@modal.fastapi_endpoint(method="POST")
def mcp_endpoint(request: dict) -> dict:
    """
    MCP Server endpoint that handles Model Context Protocol requests
    """
    try:
        # Parse MCP request
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id", 1)
        
        # Handle different MCP methods
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "romanize_text",
                            "description": "Convert text in any script to Latin alphabet",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "text": {
                                        "type": "string",
                                        "description": "Text to romanize"
                                    },
                                    "lang_code": {
                                        "type": "string",
                                        "description": "Optional ISO language code (e.g., 'rus', 'ara', 'hin')"
                                    }
                                },
                                "required": ["text"]
                            }
                        },
                        {
                            "name": "romanize_batch",
                            "description": "Romanize multiple texts at once",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "texts": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Array of texts to romanize"
                                    },
                                    "lang_code": {
                                        "type": "string",
                                        "description": "Optional ISO language code"
                                    }
                                },
                                "required": ["texts"]
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            
            if tool_name == "romanize_text":
                text = tool_args.get("text", "")
                lang_code = tool_args.get("lang_code")
                
                if not text:
                    return create_error_response(request_id, "INVALID_PARAMS", "Text is required")
                
                uroman = get_uroman()
                romanized = uroman.romanize_string(text, lang_code)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Romanized: {romanized}"
                            }
                        ],
                        "data": {
                            "original": text,
                            "romanized": romanized,
                            "lang_code": lang_code
                        }
                    }
                }
            
            elif tool_name == "romanize_batch":
                texts = tool_args.get("texts", [])
                lang_code = tool_args.get("lang_code")
                
                if not texts:
                    return create_error_response(request_id, "INVALID_PARAMS", "Texts array is required")
                
                uroman = get_uroman()
                results = []
                for text in texts:
                    romanized = uroman.romanize_string(text, lang_code)
                    results.append({
                        "original": text,
                        "romanized": romanized
                    })
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Romanized {len(results)} texts"
                            }
                        ],
                        "data": {
                            "results": results,
                            "lang_code": lang_code
                        }
                    }
                }
            
            else:
                return create_error_response(request_id, "METHOD_NOT_FOUND", f"Unknown tool: {tool_name}")
        
        else:
            return create_error_response(request_id, "METHOD_NOT_FOUND", f"Unknown method: {method}")
    
    except Exception as e:
        return create_error_response(request.get("id", 1), "INTERNAL_ERROR", str(e))

def create_error_response(request_id: int, code: str, message: str) -> dict:
    """Create MCP error response"""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32000 if code == "INTERNAL_ERROR" else -32602,
            "message": message,
            "data": {"code": code}
        }
    }

# Also keep the simple REST endpoint for backward compatibility
@app.function(image=image, scaledown_window=300)
@modal.fastapi_endpoint(method="POST")
def romanize_endpoint(item: dict) -> dict:
    """Simple REST endpoint (non-MCP)"""
    text = item.get("text", "")
    lang_code = item.get("lang_code")
    
    if not text:
        return {"error": "No text provided"}
    
    try:
        uroman = get_uroman()
        romanized = uroman.romanize_string(text, lang_code)
        return {
            "original": text,
            "romanized": romanized,
            "lang_code": lang_code
        }
    except Exception as e:
        return {"error": str(e)}

@app.local_entrypoint()
def main():
    """Test the MCP server locally"""
    print("Testing MCP Server...")
    
    # Test tools/list
    list_response = mcp_endpoint.remote({
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    })
    print(f"Tools available: {json.dumps(list_response, indent=2)}")
    
    # Test romanize_text
    romanize_response = mcp_endpoint.remote({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "romanize_text",
            "arguments": {
                "text": "Привет, MCP!",
                "lang_code": "rus"
            }
        },
        "id": 2
    })
    print(f"\nRomanize result: {json.dumps(romanize_response, indent=2, ensure_ascii=False)}")

# Replace the main function with this corrected version
if __name__ == "__main__":
    """Test the MCP server using curl commands"""
    print("MCP Server deployed!")
    print("\nTo test, use these curl commands:")
    print("\n1. List tools:")
    print('curl -X POST [YOUR-MCP-ENDPOINT-URL] \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"jsonrpc": "2.0", "method": "tools/list", "id": 1}\'')
    print("\n2. Romanize text:")
    print('curl -X POST [YOUR-MCP-ENDPOINT-URL] \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "romanize_text", "arguments": {"text": "Привет", "lang_code": "rus"}}, "id": 2}\'')
