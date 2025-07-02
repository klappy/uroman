#!/usr/bin/env python3
"""
Performance test for uroman MCP server
"""

import time
import requests
import statistics

MCP_ENDPOINT = "https://klappy--uroman-service-mcp-endpoint.modal.run"

def test_latency(n=10):
    """Test average latency"""
    print(f"Testing latency with {n} requests...")
    
    times = []
    test_texts = [
        ("Hello world", None),
        ("Привет мир", "rus"),
        ("你好世界", "zho"),
        ("مرحبا بالعالم", "ara"),
        ("नमस्ते संसार", "hin"),
    ]
    
    for i in range(n):
        text, lang = test_texts[i % len(test_texts)]
        start = time.time()
        
        response = requests.post(MCP_ENDPOINT, json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "romanize_text",
                "arguments": {
                    "text": text,
                    "lang_code": lang
                }
            },
            "id": i
        })
        
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Request {i+1}: {elapsed:.3f}s")
    
    print(f"\nPerformance Summary:")
    print(f"  Average: {statistics.mean(times):.3f}s")
    print(f"  Median: {statistics.median(times):.3f}s")
    print(f"  Min: {min(times):.3f}s")
    print(f"  Max: {max(times):.3f}s")
    print(f"  Std Dev: {statistics.stdev(times):.3f}s")

def test_batch_performance():
    """Test batch vs individual performance"""
    print("\nTesting batch vs individual performance...")
    
    texts = [
        "Hello from test " + str(i)
        for i in range(20)
    ]
    
    # Individual requests
    start = time.time()
    for text in texts:
        requests.post(MCP_ENDPOINT, json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "romanize_text",
                "arguments": {"text": text}
            },
            "id": 1
        })
    individual_time = time.time() - start
    
    # Batch request
    start = time.time()
    requests.post(MCP_ENDPOINT, json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "romanize_batch",
            "arguments": {"texts": texts}
        },
        "id": 2
    })
    batch_time = time.time() - start
    
    print(f"  Individual (20 requests): {individual_time:.2f}s")
    print(f"  Batch (1 request): {batch_time:.2f}s")
    print(f"  Speedup: {individual_time/batch_time:.1f}x")

if __name__ == "__main__":
    print("🏃 Uroman MCP Server Performance Test")
    print("=" * 40)
    test_latency()
    test_batch_performance()
