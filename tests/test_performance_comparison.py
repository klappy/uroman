#!/usr/bin/env python3
"""
Performance comparison between local and remote uroman
"""

import sys
import time
import requests
import statistics
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent))
import uroman

# Endpoints
REST_ENDPOINT = "https://klappy--uroman-service-romanize-endpoint.modal.run"
TEXT_DIR = Path(__file__).parent.parent / "text"

def run_comparison():
    """Compare local vs remote performance"""
    print("🔄 Local vs Remote Performance Comparison")
    print("=" * 60)
    
    # Initialize local uroman
    local_uroman = uroman.Uroman()
    
    # Collect test texts from all languages
    test_samples = []
    for file_path in TEXT_DIR.glob("*.txt"):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.readline().strip()
            if text and len(text) < 200:
                test_samples.append((text, file_path.stem))
    
    test_samples = test_samples[:15]  # Test 15 diverse samples
    
    print(f"Testing with {len(test_samples)} samples from different languages\n")
    
    # Test LOCAL performance
    print("📍 Testing LOCAL performance...")
    local_times = []
    for text, lang in test_samples:
        start = time.time()
        result = local_uroman.romanize_string(text)
        elapsed = time.time() - start
        local_times.append(elapsed)
        print(f"  {lang}: {elapsed*1000:.1f}ms")
    
    # Test REMOTE performance
    print("\n☁️  Testing REMOTE performance...")
    remote_times = []
    for text, lang in test_samples:
        start = time.time()
        response = requests.post(REST_ENDPOINT, json={"text": text})
        elapsed = time.time() - start
        remote_times.append(elapsed)
        print(f"  {lang}: {elapsed*1000:.1f}ms")
    
    # Calculate statistics
    print("\n📊 Performance Summary")
    print("=" * 60)
    
    print("\nLocal Performance:")
    print(f"  Average: {statistics.mean(local_times)*1000:.1f}ms")
    print(f"  Median: {statistics.median(local_times)*1000:.1f}ms")
    print(f"  Min: {min(local_times)*1000:.1f}ms")
    print(f"  Max: {max(local_times)*1000:.1f}ms")
    print(f"  Std Dev: {statistics.stdev(local_times)*1000:.1f}ms")
    
    print("\nRemote Performance:")
    print(f"  Average: {statistics.mean(remote_times)*1000:.1f}ms")
    print(f"  Median: {statistics.median(remote_times)*1000:.1f}ms")
    print(f"  Min: {min(remote_times)*1000:.1f}ms")
    print(f"  Max: {max(remote_times)*1000:.1f}ms")
    print(f"  Std Dev: {statistics.stdev(remote_times)*1000:.1f}ms")
    
    print("\nComparison:")
    avg_local = statistics.mean(local_times)*1000
    avg_remote = statistics.mean(remote_times)*1000
    print(f"  Network overhead: {avg_remote - avg_local:.1f}ms")
    print(f"  Remote is {avg_remote/avg_local:.1f}x slower than local")
    print(f"  Local processes at {1000/avg_local:.1f} texts/second")
    print(f"  Remote processes at {1000/avg_remote:.1f} texts/second")
    
    # Throughput test
    print("\n🚀 Throughput Test (10 seconds each)")
    print("=" * 60)
    
    test_text = "Hello Привет 你好 مرحبا नमस्ते"
    duration = 10
    
    # Local throughput
    print(f"Testing local throughput for {duration}s...")
    count = 0
    start = time.time()
    while time.time() - start < duration:
        local_uroman.romanize_string(test_text)
        count += 1
    local_rps = count / duration
    print(f"  Local: {local_rps:.1f} requests/second")
    
    # Remote throughput (with concurrency)
    print(f"Testing remote throughput for {duration}s...")
    count = 0
    errors = 0
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        while time.time() - start < duration:
            future = executor.submit(requests.post, REST_ENDPOINT, json={"text": test_text})
            futures.append(future)
            count += 1
            time.sleep(0.05)  # Rate limit
        
        # Wait for completion
        for future in as_completed(futures):
            try:
                future.result()
            except:
                errors += 1
    
    remote_rps = count / duration
    print(f"  Remote: {remote_rps:.1f} requests/second (errors: {errors})")
    print(f"  Local is {local_rps/remote_rps:.1f}x faster for throughput")
    
    print("\n✅ Comparison complete!")

if __name__ == "__main__":
    run_comparison()
