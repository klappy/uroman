"""AWS Lambda adapter for uroman serverless"""

import json
from typing import Any, Dict, Optional
from .base_adapter import ServerlessAdapter


class AWSLambdaAdapter(ServerlessAdapter):
    """Adapter for AWS Lambda platform"""
    
    def handle_http_request(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Handle AWS Lambda HTTP request (API Gateway format)"""
        # Parse the body from API Gateway event
        body_str = event.get('body', '{}')
        body = self.parse_json_body(body_str)
        
        # Process the request
        result = self.handler.handle_request(body)
        
        # Create Lambda response
        return self.create_http_response(200, result)
    
    def handle_mcp_request(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Handle AWS Lambda MCP request"""
        # Parse the body
        body_str = event.get('body', '{}')
        body = self.parse_json_body(body_str)
        
        # Process MCP request
        result = self.mcp_handler.handle_mcp_request(body)
        
        # Create Lambda response
        return self.create_http_response(200, result)
    
    def create_http_response(self, status_code: int, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create AWS Lambda response format"""
        response_headers = self.get_default_headers()
        if headers:
            response_headers.update(headers)
        
        return {
            'statusCode': status_code,
            'headers': response_headers,
            'body': json.dumps(body)
        }
    
    def create_lambda_handler(self, handler_type: str = "http"):
        """Create Lambda handler function"""
        adapter = self
        
        if handler_type == "mcp":
            def lambda_handler(event, context):
                return adapter.handle_mcp_request(event, context)
        else:
            def lambda_handler(event, context):
                return adapter.handle_http_request(event, context)
        
        return lambda_handler
