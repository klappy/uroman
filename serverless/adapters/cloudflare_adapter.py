"""
Cloudflare Workers adapter for uroman serverless

⚠️ WARNING: This adapter is provided for reference only.
Cloudflare Workers CANNOT run uroman due to platform limitations:
- 10MB size limit (uroman needs 13-15MB)
- No regex module support
- Limited Python support

See serverless/deployments/cloudflare/LIMITATIONS.md for details.

DO NOT attempt to deploy uroman on Cloudflare Workers.
Use Modal.ai or AWS Lambda instead.
"""

import json
from typing import Any, Dict, Optional
from .base_adapter import ServerlessAdapter


class CloudflareAdapter(ServerlessAdapter):
    """
    Adapter for Cloudflare Workers platform
    
    ⚠️ NOT FUNCTIONAL - Cloudflare Workers cannot support uroman's requirements.
    This code is kept for reference only.
    """
    
    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "Cloudflare Workers cannot support uroman due to platform limitations:\n"
            "- 10MB size limit (uroman needs 13-15MB)\n"
            "- No regex module (only basic re)\n"
            "- Limited Python support (experimental)\n"
            "\nUse Modal.ai or AWS Lambda instead."
        )
    
    def handle_http_request(self, request: Any, env: Any, ctx: Any) -> Any:
        """Handle Cloudflare Workers request - NOT IMPLEMENTED"""
        raise NotImplementedError("Cloudflare Workers cannot run uroman")
    
    def handle_mcp_request(self, request: Any, env: Any, ctx: Any) -> Any:
        """Handle Cloudflare Workers MCP request - NOT IMPLEMENTED"""
        raise NotImplementedError("Cloudflare Workers cannot run uroman")
    
    def create_http_response(self, status_code: int, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create response format for Cloudflare Workers - NOT IMPLEMENTED"""
        raise NotImplementedError("Cloudflare Workers cannot run uroman")
