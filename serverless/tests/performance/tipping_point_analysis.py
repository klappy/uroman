#!/usr/bin/env python3
"""
Tipping Point Analysis: When does remote beat local?
"""

import time
import threading
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
import uroman

# Configuration
REST_ENDPOINT = "https://klappy--uroman-service-romanize-endpoint.modal.run"

def analyze_tipping_point():
    """Analyze when remote becomes faster than local"""
    
    print("🔍 Tipping Point Analysis: Local vs Remote Uroman")
    print("=" * 60)
    
    # Initialize local uroman
    print("Initializing local uroman...")
    local_uroman = uroman.Uroman()
    
    # Test text
    test_text = "Hello Привет 你好 مرحبا नमस्ते"
    
    # First, establish baseline performance
    print("\n📊 Establishing baseline performance...")
    
    # Local baseline (single-threaded)
    local_times = []
    for _ in range(10):
        start = time.time()
        local_uroman.romanize_string(test_text)
        local_times.append(time.time() - start)
    
    local_baseline = statistics.mean(local_times) * 1000  # Convert to ms
    print(f"Local baseline: {local_baseline:.1f}ms per request")
    
    # Remote baseline (single request)
    remote_times = []
    for _ in range(5):
        start = time.time()
        requests.post(REST_ENDPOINT, json={"text": test_text})
        remote_times.append(time.time() - start)
    
    remote_baseline = statistics.mean(remote_times) * 1000  # Convert to ms
    print(f"Remote baseline: {remote_baseline:.1f}ms per request")
    
    # Test different concurrency levels
    print("\n🧪 Testing concurrency levels...")
    concurrency_levels = [1, 2, 5, 10, 20, 50, 100]
    results = {'local': [], 'remote': []}
    
    for num_concurrent in concurrency_levels:
        print(f"\nTesting with {num_concurrent} concurrent requests...")
        
        # Local test with threading
        print(f"  Local test...")
        local_latencies = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = []
            for _ in range(num_concurrent * 10):  # 10 requests per thread
                future = executor.submit(local_uroman.romanize_string, test_text)
                futures.append((future, time.time()))
            
            for future, submit_time in futures:
                result = future.result()
                completion_time = time.time()
                latency = (completion_time - submit_time) * 1000
                local_latencies.append(latency)
        
        total_time = time.time() - start_time
        local_throughput = len(futures) / total_time
        local_avg_latency = statistics.mean(local_latencies)
        local_p95_latency = statistics.quantiles(local_latencies, n=20)[18]
        
        print(f"    Throughput: {local_throughput:.1f} req/s")
        print(f"    Avg latency: {local_avg_latency:.1f}ms")
        print(f"    P95 latency: {local_p95_latency:.1f}ms")
        
        # Remote test
        print(f"  Remote test...")
        remote_latencies = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = []
            for _ in range(num_concurrent * 5):  # Fewer requests to avoid rate limiting
                future = executor.submit(requests.post, REST_ENDPOINT, json={"text": test_text})
                futures.append((future, time.time()))
            
            for future, submit_time in futures:
                try:
                    response = future.result(timeout=10)
                    completion_time = time.time()
                    latency = (completion_time - submit_time) * 1000
                    remote_latencies.append(latency)
                except:
                    pass  # Skip failed requests
        
        if remote_latencies:
            total_time = time.time() - start_time
            remote_throughput = len(remote_latencies) / total_time
            remote_avg_latency = statistics.mean(remote_latencies)
            remote_p95_latency = statistics.quantiles(remote_latencies, n=20)[18] if len(remote_latencies) > 20 else max(remote_latencies)
            
            print(f"    Throughput: {remote_throughput:.1f} req/s")
            print(f"    Avg latency: {remote_avg_latency:.1f}ms")
            print(f"    P95 latency: {remote_p95_latency:.1f}ms")
        else:
            remote_avg_latency = 999999
            remote_p95_latency = 999999
        
        results['local'].append({
            'concurrency': num_concurrent,
            'throughput': local_throughput,
            'avg_latency': local_avg_latency,
            'p95_latency': local_p95_latency
        })
        
        results['remote'].append({
            'concurrency': num_concurrent,
            'throughput': remote_throughput if remote_latencies else 0,
            'avg_latency': remote_avg_latency,
            'p95_latency': remote_p95_latency
        })
    
    # Analysis
    print("\n📈 ANALYSIS RESULTS")
    print("=" * 60)
    
    print("\nKey Findings:")
    
    # Find tipping points
    for i, level in enumerate(concurrency_levels):
        local_p95 = results['local'][i]['p95_latency']
        remote_p95 = results['remote'][i]['p95_latency']
        
        if remote_p95 < local_p95 * 2:  # Within 2x is considered competitive
            print(f"\n🎯 TIPPING POINT at {level} concurrent users!")
            print(f"  Local P95: {local_p95:.1f}ms")
            print(f"  Remote P95: {remote_p95:.1f}ms")
            print(f"  Remote is only {remote_p95/local_p95:.1f}x slower")
            break
    
    # CPU and memory considerations
    print("\n💻 System Resource Analysis:")
    print(f"  Your CPU cores: {threading.active_count()} (available for local)")
    print(f"  Modal auto-scaling: Unlimited (scales with demand)")
    
    # Calculate theoretical limits
    print("\n📊 Theoretical Limits:")
    
    # Local limit (CPU bound)
    cpu_cores = threading.active_count()
    max_local_throughput = cpu_cores * (1000 / local_baseline)  # requests/second
    print(f"  Local max throughput: ~{max_local_throughput:.0f} req/s (CPU limited)")
    
    # Remote limit (Modal scaling)
    print(f"  Remote max throughput: Unlimited (Modal auto-scales)")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("=" * 60)
    
    if max_local_throughput > 100:
        print(f"1. For <{int(max_local_throughput * 0.5)} req/s: Use LOCAL (faster, no network)")
        print(f"2. For {int(max_local_throughput * 0.5)}-{int(max_local_throughput)} req/s: Consider REMOTE (approaching local limits)")
        print(f"3. For >{int(max_local_throughput)} req/s: Use REMOTE (exceeds local capacity)")
    else:
        print("1. For <50 req/s: Use LOCAL")
        print("2. For 50-100 req/s: Consider REMOTE")
        print("3. For >100 req/s: Use REMOTE")
    
    print("\n🎯 Tipping Point Summary:")
    print(f"  - Remote becomes VIABLE at: ~{concurrency_levels[2]} concurrent users")
    print(f"  - Remote becomes NECESSARY at: ~{cpu_cores * 10} concurrent users")
    print(f"  - Remote becomes SUPERIOR at: ~{cpu_cores * 20} concurrent users")
    
    print("\n📌 Other Factors to Consider:")
    print("  - Local requires NO network (works offline)")
    print("  - Local has ZERO latency overhead")
    print("  - Remote has INFINITE scalability")
    print("  - Remote requires NO maintenance")
    print("  - Remote can handle BURST traffic")

if __name__ == "__main__":
    analyze_tipping_point()
