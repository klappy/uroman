#!/usr/bin/env python3
"""
Compare performance between REST and MCP endpoints
"""

import requests
import time
import statistics
import json

REST_ENDPOINT = "https://klappy--uroman-service-romanize-endpoint.modal.run"
MCP_ENDPOINT = "https://klappy--uroman-service-mcp-endpoint.modal.run"

def test_rest_endpoint(text, lang_code=None):
    """Test REST endpoint performance"""
    start = time.time()
    response = requests.post(REST_ENDPOINT, json={
        "text": text,
        "lang_code": lang_code
    })
    elapsed = time.time() - start
    return elapsed, response.json()

def test_mcp_endpoint(text, lang_code=None):
    """Test MCP endpoint performance"""
    start = time.time()
    response = requests.post(MCP_ENDPOINT, json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "romanize_text",
            "arguments": {
                "text": text,
                "lang_code": lang_code
            }
        },
        "id": 1
    })
    elapsed = time.time() - start
    data = response.json()
    # Extract the romanized text from MCP response
    result = {
        "romanized": data["result"]["data"]["romanized"],
        "original": data["result"]["data"]["original"]
    }
    return elapsed, result

def compare_performance(iterations=10):
    """Compare both endpoints"""
    test_text = "Hello мир 世界 مرحبا"
    
    print(f"🏃 Comparing REST vs MCP endpoints ({iterations} iterations each)\n")
    
    # Warm up both endpoints
    print("Warming up endpoints...")
    test_rest_endpoint(test_text)
    test_mcp_endpoint(test_text)
    
    # Test REST endpoint
    print("\n📊 Testing REST endpoint...")
    rest_times = []
    for i in range(iterations):
        elapsed, result = test_rest_endpoint(test_text)
        rest_times.append(elapsed)
        print(f"  Request {i+1}: {elapsed:.3f}s")
    
    # Test MCP endpoint
    print("\n📊 Testing MCP endpoint...")
    mcp_times = []
    for i in range(iterations):
        elapsed, result = test_mcp_endpoint(test_text)
        mcp_times.append(elapsed)
        print(f"  Request {i+1}: {elapsed:.3f}s")
    
    # Calculate statistics
    print("\n📈 Performance Summary:")
    print(f"\nREST Endpoint:")
    print(f"  Average: {statistics.mean(rest_times):.3f}s")
    print(f"  Median: {statistics.median(rest_times):.3f}s")
    print(f"  Min: {min(rest_times):.3f}s")
    print(f"  Max: {max(rest_times):.3f}s")
    print(f"  Std Dev: {statistics.stdev(rest_times):.3f}s")
    
    print(f"\nMCP Endpoint:")
    print(f"  Average: {statistics.mean(mcp_times):.3f}s")
    print(f"  Median: {statistics.median(mcp_times):.3f}s")
    print(f"  Min: {min(mcp_times):.3f}s")
    print(f"  Max: {max(mcp_times):.3f}s")
    print(f"  Std Dev: {statistics.stdev(mcp_times):.3f}s")
    
    # Comparison
    avg_diff = statistics.mean(mcp_times) - statistics.mean(rest_times)
    percent_diff = (avg_diff / statistics.mean(rest_times)) * 100
    
    print(f"\n🔍 Comparison:")
    print(f"  MCP overhead: {avg_diff:.3f}s ({percent_diff:+.1f}%)")
    
    # Payload size comparison
    print(f"\n📦 Payload Size Comparison:")
    rest_payload = json.dumps({"text": test_text, "lang_code": None})
    mcp_payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "romanize_text",
            "arguments": {"text": test_text, "lang_code": None}
        },
        "id": 1
    })
    print(f"  REST payload: {len(rest_payload)} bytes")
    print(f"  MCP payload: {len(mcp_payload)} bytes")
    print(f"  MCP overhead: {len(mcp_payload) - len(rest_payload)} bytes")

if __name__ == "__main__":
    compare_performance(10)
