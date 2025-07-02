"""MCP (Model Context Protocol) handler - platform agnostic"""

from typing import Dict, Any, Optional, List
from .romanizer_service import RomanizerService


class MCPHandler:
    """Handles MCP protocol requests for AI assistants"""
    
    def __init__(self, romanizer_service: Optional[RomanizerService] = None):
        self.service = romanizer_service or RomanizerService()
        
    def handle_tools_list(self) -> Dict[str, Any]:
        """Return available MCP tools"""
        return {
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
    
    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool calls"""
        if tool_name == "romanize_text":
            text = arguments.get("text", "")
            if not text:
                return self._error_response("Text is required", "INVALID_PARAMS")
            
            try:
                romanized = self.service.romanize(text, arguments.get("lang_code"))
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Romanized: {romanized}"
                    }],
                    "data": {
                        "original": text,
                        "romanized": romanized,
                        "lang_code": arguments.get("lang_code")
                    }
                }
            except Exception as e:
                return self._error_response(str(e), "ROMANIZATION_ERROR")
                
        elif tool_name == "romanize_batch":
            texts = arguments.get("texts", [])
            if not texts:
                return self._error_response("Texts array is required", "INVALID_PARAMS")
            
            try:
                romanized_texts = self.service.romanize_batch(texts, arguments.get("lang_code"))
                results = [f"{orig} → {rom}" for orig, rom in zip(texts, romanized_texts)]
                return {
                    "content": [{
                        "type": "text",
                        "text": "Romanized:\n" + "\n".join(results)
                    }],
                    "data": {
                        "originals": texts,
                        "romanized": romanized_texts,
                        "lang_code": arguments.get("lang_code"),
                        "count": len(texts)
                    }
                }
            except Exception as e:
                return self._error_response(str(e), "BATCH_ERROR")
        
        else:
            return self._error_response(f"Unknown tool: {tool_name}", "METHOD_NOT_FOUND")
    
    def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic MCP request"""
        method = request.get("method", "")
        request_id = request.get("id", 1)
        
        try:
            if method == "tools/list":
                result = self.handle_tools_list()
            elif method == "tools/call":
                params = request.get("params", {})
                result = self.handle_tool_call(
                    params.get("name", ""),
                    params.get("arguments", {})
                )
            else:
                return self._jsonrpc_error(request_id, f"Unknown method: {method}", -32601)
            
            # Wrap in JSON-RPC response
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
        except Exception as e:
            return self._jsonrpc_error(request_id, str(e), -32603)
    
    def _error_response(self, message: str, code: str) -> Dict[str, Any]:
        """Create MCP error response"""
        return {
            "error": {
                "message": message,
                "code": code
            }
        }
    
    def _jsonrpc_error(self, request_id: Any, message: str, code: int) -> Dict[str, Any]:
        """Create JSON-RPC error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message,
                "data": {"code": "METHOD_NOT_FOUND" if code == -32601 else "INTERNAL_ERROR"}
            }
        }
