"""Test suite for serverless adapters"""

import pytest
import json
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serverless.adapters.modal_adapter import ModalAdapter
from serverless.adapters.aws_lambda_adapter import AWSLambdaAdapter


class TestAdapters:
    """Test all adapter implementations"""
    
    @pytest.fixture
    def modal_adapter(self):
        return ModalAdapter()
    
    @pytest.fixture
    def aws_adapter(self):
        return AWSLambdaAdapter()
    
    def test_modal_http_request(self, modal_adapter):
        """Test Modal HTTP request handling"""
        # Modal passes dict directly
        event = {
            "text": "Привет мир",
            "lang_code": "rus"
        }
        
        result = modal_adapter.handle_http_request(event)
        
        assert result["romanized"] == "Privet mir"
        assert result["original"] == "Привет мир"
        assert result["lang_code"] == "rus"
    
    def test_aws_http_request(self, aws_adapter):
        """Test AWS Lambda HTTP request handling"""
        # AWS API Gateway event format
        event = {
            "body": json.dumps({
                "text": "Привет мир",
                "lang_code": "rus"
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }
        
        result = aws_adapter.handle_http_request(event, None)
        
        assert result["statusCode"] == 200
        assert "body" in result
        body = json.loads(result["body"])
        assert body["romanized"] == "Privet mir"
    
    def test_modal_mcp_request(self, modal_adapter):
        """Test Modal MCP request handling"""
        event = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }
        
        result = modal_adapter.handle_mcp_request(event)
        
        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 1
        assert "result" in result
        assert len(result["result"]["tools"]) == 2
    
    def test_aws_mcp_request(self, aws_adapter):
        """Test AWS Lambda MCP request handling"""
        event = {
            "body": json.dumps({
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1
            })
        }
        
        result = aws_adapter.handle_mcp_request(event, None)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["jsonrpc"] == "2.0"
        assert len(body["result"]["tools"]) == 2
    
    def test_batch_processing(self, modal_adapter, aws_adapter):
        """Test batch processing across adapters"""
        batch_request = {
            "texts": ["Hello", "Привет", "你好"],
            "lang_code": None
        }
        
        # Test Modal
        modal_result = modal_adapter.handle_http_request(batch_request)
        assert len(modal_result["romanized"]) == 3
        assert modal_result["romanized"][1] == "Privet"
        
        # Test AWS
        aws_event = {"body": json.dumps(batch_request)}
        aws_result = aws_adapter.handle_http_request(aws_event, None)
        aws_body = json.loads(aws_result["body"])
        assert len(aws_body["romanized"]) == 3
        assert aws_body["romanized"][1] == "Privet"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
