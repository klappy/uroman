"""Base adapter class for serverless platforms"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..core import UromanHandler, MCPHandler, RomanizerService


class ServerlessAdapter(ABC):
    """Abstract base class for serverless platform adapters"""
    
    def __init__(self, uroman_path: Optional[str] = None):
        self.service = RomanizerService(uroman_path)
        self.handler = UromanHandler(self.service)
        self.mcp_handler = MCPHandler(self.service)
    
    @abstractmethod
    def handle_http_request(self, event: Any, context: Any) -> Any:
        """Handle HTTP request in platform-specific format"""
        pass
    
    @abstractmethod
    def handle_mcp_request(self, event: Any, context: Any) -> Any:
        """Handle MCP request in platform-specific format"""
        pass
    
    @abstractmethod
    def create_http_response(self, status_code: int, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Any:
        """Create platform-specific HTTP response"""
        pass
    
    def get_default_headers(self) -> Dict[str, str]:
        """Get default response headers"""
        return {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    
    def parse_json_body(self, body: Any) -> Dict[str, Any]:
        """Parse JSON body from various formats"""
        import json
        
        if isinstance(body, str):
            return json.loads(body)
        elif isinstance(body, dict):
            return body
        else:
            return {}
