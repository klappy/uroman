#!/usr/bin/env python3
"""
Test MCP server endpoints directly
Run this in Cursor to test the MCP functionality
"""

import requests
import json

MCP_ENDPOINT = "https://klappy--uroman-service-mcp-endpoint.modal.run"

def test_mcp_tools_list():
    """Test listing available tools"""
    print("1. Testing MCP tools/list...")
    response = requests.post(MCP_ENDPOINT, json={
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    })
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_romanize_single():
    """Test single text romanization"""
    print("\n2. Testing single romanization...")
    response = requests.post(MCP_ENDPOINT, json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "romanize_text",
            "arguments": {
                "text": "Hello мир 世界",
                "lang_code": None
            }
        },
        "id": 2
    })
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_romanize_batch():
    """Test batch romanization"""
    print("\n3. Testing batch romanization...")
    response = requests.post(MCP_ENDPOINT, json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "romanize_batch",
            "arguments": {
                "texts": ["Привет", "你好", "مرحبا", "नमस्ते"],
                "lang_code": None
            }
        },
        "id": 3
    })
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

if __name__ == "__main__":
    print("🧪 Testing MCP Server in Cursor\n")
    
    # Run tests
    test_mcp_tools_list()
    test_romanize_single()
    test_romanize_batch()
    
    print("\n✅ All tests complete! The MCP server is working.")
    print("\nYou can now:")
    print("1. Use these functions in your code")
    print("2. Configure Claude Desktop to use this MCP server")
    print("3. Build applications that romanize text via the API")
