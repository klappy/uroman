#!/usr/bin/env python3
"""
Comprehensive load testing for uroman MCP server
Tests with real-world examples from all languages
"""

import time
import requests
import statistics
import concurrent.futures
import json
from pathlib import Path
from collections import defaultdict
import threading

# Configuration
MCP_ENDPOINT = "https://klappy--uroman-mcp-server-mcp-endpoint.modal.run"
REST_ENDPOINT = "https://klappy--uroman-mcp-server-romanize-endpoint.modal.run"

# Thread-safe counters
request_times = []
request_lock = threading.Lock()
error_count = 0
success_count = 0

def load_all_test_data():
    """Load all test data from text files"""
    test_data = {}
    text_dir = Path("../text")
    
    lang_names = {
        'amh': 'Amharic',
        'ara': 'Arabic', 
        'ben': 'Bengali',
        'bod': 'Tibetan',
        'egy': 'Egyptian',
        'ell': 'Greek',
        'fas': 'Persian',
        'heb': 'Hebrew',
        'hin': 'Hindi',
        'jpn': 'Japanese',
        'kor': 'Korean',
        'mar': 'Marathi',
        'mya': 'Myanmar',
        'nep': 'Nepali',
        'rus': 'Russian',
        'tam': 'Tamil',
        'tha': 'Thai',
        'tlh': 'Klingon',
        'tur': 'Turkish',
        'tzm': 'Tamazight',
        'uig': 'Uyghur',
        'zho': 'Chinese',
        'multiple': 'Mixed Scripts'
    }
    
    for lang_file in sorted(text_dir.glob("*.txt")):
        lang_code = lang_file.stem
        lang_name = lang_names.get(lang_code, lang_code)
        
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                if lines:
                    test_data[lang_code] = {
                        'name': lang_name,
                        'samples': lines[:10]  # Take up to 10 samples
                    }
        except Exception as e:
            print(f"Error loading {lang_file}: {e}")
    
    return test_data

def make_mcp_request(text, lang_code=None, request_id=1):
    """Make a single MCP request and measure time"""
    global error_count, success_count
    
    start_time = time.time()
    try:
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
            "id": request_id
        }, timeout=10)
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if 'error' not in data:
                with request_lock:
                    request_times.append(elapsed)
                    success_count += 1
                return elapsed, data.get('result', {}).get('data', {}).get('romanized', '')
            else:
                with request_lock:
                    error_count += 1
                return elapsed, f"Error: {data['error']}"
        else:
            with request_lock:
                error_count += 1
            return elapsed, f"HTTP {response.status_code}"
    except Exception as e:
        with request_lock:
            error_count += 1
        return time.time() - start_time, f"Exception: {str(e)}"

def load_test_sequential(test_data, samples_per_lang=3):
    """Sequential load test"""
    print("\n📊 Sequential Load Test")
    print("=" * 60)
    
    total_requests = sum(min(len(data['samples']), samples_per_lang) for data in test_data.values())
    print(f"Testing {total_requests} requests sequentially...")
    
    start_time = time.time()
    results = []
    
    for lang_code, data in test_data.items():
        for i, text in enumerate(data['samples'][:samples_per_lang]):
            elapsed, result = make_mcp_request(text, lang_code if lang_code != 'multiple' else None)
            results.append({
                'lang': data['name'],
                'text': text[:50] + '...' if len(text) > 50 else text,
                'romanized': result[:50] + '...' if len(result) > 50 else result,
                'time': elapsed
            })
            print(f"  {data['name']}: {elapsed:.3f}s")
    
    total_time = time.time() - start_time
    
    print(f"\nSequential Results:")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Requests/second: {len(results)/total_time:.2f}")
    print(f"  Average latency: {statistics.mean(r['time'] for r in results):.3f}s")
    
    return results

def load_test_concurrent(test_data, workers=10, samples_per_lang=5):
    """Concurrent load test"""
    print("\n🚀 Concurrent Load Test")
    print("=" * 60)
    
    # Prepare all requests
    all_requests = []
    for lang_code, data in test_data.items():
        for text in data['samples'][:samples_per_lang]:
            all_requests.append((text, lang_code if lang_code != 'multiple' else None, data['name']))
    
    print(f"Testing {len(all_requests)} requests with {workers} concurrent workers...")
    
    # Reset counters
    global request_times, error_count, success_count
    request_times = []
    error_count = 0
    success_count = 0
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for i, (text, lang_code, lang_name) in enumerate(all_requests):
            future = executor.submit(make_mcp_request, text, lang_code, i)
            futures.append((future, lang_name, text))
        
        # Collect results
        results = []
        for future, lang_name, text in futures:
            elapsed, result = future.result()
            results.append({
                'lang': lang_name,
                'text': text[:30] + '...' if len(text) > 30 else text,
                'time': elapsed
            })
    
    total_time = time.time() - start_time
    
    print(f"\nConcurrent Results:")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Total requests: {len(all_requests)}")
    print(f"  Successful: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Requests/second: {success_count/total_time:.2f}")
    print(f"  Average latency: {statistics.mean(request_times):.3f}s")
    print(f"  Median latency: {statistics.median(request_times):.3f}s")
    print(f"  P95 latency: {statistics.quantiles(request_times, n=20)[18]:.3f}s")
    print(f"  P99 latency: {statistics.quantiles(request_times, n=100)[98]:.3f}s")

def load_test_batch(test_data):
    """Test batch processing performance"""
    print("\n📦 Batch Processing Test")
    print("=" * 60)
    
    # Collect texts from all languages
    all_texts = []
    for data in test_data.values():
        all_texts.extend(data['samples'][:2])  # 2 samples per language
    
    print(f"Testing batch of {len(all_texts)} texts...")
    
    start_time = time.time()
    
    response = requests.post(MCP_ENDPOINT, json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "romanize_batch",
            "arguments": {
                "texts": all_texts
            }
        },
        "id": 1
    })
    
    batch_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        if 'result' in data:
            results = data['result']['data']['results']
            print(f"  Batch processing time: {batch_time:.2f}s")
            print(f"  Texts/second: {len(all_texts)/batch_time:.2f}")
            print(f"  Average per text: {batch_time/len(all_texts)*1000:.1f}ms")
        else:
            print(f"  Error: {data.get('error', 'Unknown error')}")
    else:
        print(f"  HTTP Error: {response.status_code}")

def stress_test(duration_seconds=30):
    """Continuous stress test"""
    print(f"\n💪 Stress Test ({duration_seconds}s)")
    print("=" * 60)
    
    test_texts = [
        ("Hello world", None),
        ("Привет мир", "rus"),
        ("你好世界", "zho"),
        ("مرحبا بالعالم", "ara"),
        ("नमस्ते संसार", "hin"),
        ("こんにちは世界", "jpn"),
        ("안녕하세요 세계", "kor"),
        ("Γειά σου κόσμε", "ell"),
    ]
    
    # Reset counters
    global request_times, error_count, success_count
    request_times = []
    error_count = 0
    success_count = 0
    
    start_time = time.time()
    request_count = 0
    
    print(f"Running continuous requests for {duration_seconds} seconds...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        
        while time.time() - start_time < duration_seconds:
            text, lang = test_texts[request_count % len(test_texts)]
            future = executor.submit(make_mcp_request, text, lang, request_count)
            futures.append(future)
            request_count += 1
            time.sleep(0.05)  # 20 requests per second target
        
        # Wait for all to complete
        concurrent.futures.wait(futures)
    
    elapsed = time.time() - start_time
    
    print(f"\nStress Test Results:")
    print(f"  Duration: {elapsed:.1f}s")
    print(f"  Total requests: {request_count}")
    print(f"  Successful: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Success rate: {(success_count/request_count)*100:.1f}%")
    print(f"  Requests/second: {success_count/elapsed:.2f}")
    if request_times:
        print(f"  Average latency: {statistics.mean(request_times):.3f}s")
        print(f"  P95 latency: {statistics.quantiles(request_times, n=20)[18]:.3f}s")
        print(f"  P99 latency: {statistics.quantiles(request_times, n=100)[98]:.3f}s")

def main():
    """Run comprehensive load tests"""
    print("🔥 Comprehensive Load Testing Suite for Uroman MCP Server")
    print("=" * 60)
    
    # Load test data
    print("Loading test data from all languages...")
    test_data = load_all_test_data()
    print(f"Loaded {len(test_data)} languages with {sum(len(d['samples']) for d in test_data.values())} total samples")
    
    # Run different types of load tests
    load_test_sequential(test_data, samples_per_lang=2)
    load_test_concurrent(test_data, workers=10, samples_per_lang=3)
    load_test_batch(test_data)
    stress_test(duration_seconds=20)
    
    print("\n" + "=" * 60)
    print("🏁 Load Testing Complete!")

if __name__ == "__main__":
    main()
