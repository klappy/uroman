"""Modal.ai adapter for uroman serverless"""

import json
from typing import Any, Dict, Optional
from .base_adapter import ServerlessAdapter


class ModalAdapter(ServerlessAdapter):
    """Adapter for Modal.ai platform"""
    
    def handle_http_request(self, event: Any, context: Any = None) -> Any:
        """Handle Modal HTTP request (FastAPI format)"""
        # Modal passes the request body directly as a dict
        body = event if isinstance(event, dict) else {}
        
        # Process the request
        result = self.handler.handle_request(body)
        
        # Modal FastAPI endpoints return dict directly
        return result
    
    def handle_mcp_request(self, event: Any, context: Any = None) -> Any:
        """Handle Modal MCP request"""
        # Modal passes the request body directly
        body = event if isinstance(event, dict) else {}
        
        # Process MCP request
        result = self.mcp_handler.handle_mcp_request(body)
        
        # Return directly for Modal
        return result
    
    def create_http_response(self, status_code: int, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Any:
        """Modal handles responses differently - just return the body"""
        # Modal FastAPI endpoints handle status codes via exceptions
        # For normal responses, just return the body
        return body
    
    def create_modal_function(self, image, app):
        """Create Modal function with the adapter"""
        import modal
        
        # Create a closure that captures self
        adapter = self
        
        @app.function(image=image, scaledown_window=300)
        @modal.fastapi_endpoint(method="POST")
        def romanize_endpoint(item: dict) -> dict:
            return adapter.handle_http_request(item)
        
        @app.function(image=image, scaledown_window=300)
        @modal.fastapi_endpoint(method="POST")
        def mcp_endpoint(item: dict) -> dict:
            return adapter.handle_mcp_request(item)
        
        return romanize_endpoint, mcp_endpoint
