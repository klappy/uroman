"""Cloudflare Workers adapter for uroman serverless"""

import json
from typing import Any, Dict, Optional
from .base_adapter import ServerlessAdapter


class CloudflareAdapter(ServerlessAdapter):
    """Adapter for Cloudflare Workers platform"""
    
    def handle_http_request(self, request: Any, env: Any, ctx: Any) -> Any:
        """Handle Cloudflare Workers request"""
        # Note: This is a Python adapter that would be called from a JS wrapper
        # since Cloudflare Workers primarily supports JavaScript
        
        # Parse JSON body from request
        body = request.get('body', {})
        
        # Process the request
        result = self.handler.handle_request(body)
        
        # Return result (JS wrapper will create Response)
        return result
    
    def handle_mcp_request(self, request: Any, env: Any, ctx: Any) -> Any:
        """Handle Cloudflare Workers MCP request"""
        body = request.get('body', {})
        result = self.mcp_handler.handle_mcp_request(body)
        return result
    
    def create_http_response(self, status_code: int, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create response format for Cloudflare Workers"""
        # Return data that JS wrapper will use to create Response
        return {
            'status': status_code,
            'headers': headers or self.get_default_headers(),
            'body': body
        }
