#!/usr/bin/env python3
"""
Simple tipping point analysis
"""

import os
import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import uroman

REST_ENDPOINT = "https://klappy--uroman-mcp-server-romanize-endpoint.modal.run"

def main():
    print("🔍 Tipping Point Analysis: Local vs Remote")
    print("=" * 60)
    
    # System info
    cpu_count = os.cpu_count()
    print(f"\nYour System:")
    print(f"  CPU cores: {cpu_count}")
    print(f"  Max useful threads: ~{cpu_count * 2}")
    
    # Initialize local
    local_uroman = uroman.Uroman()
    test_text = "Hello world from tipping point analysis"
    
    # Warm up both systems
    print("\nWarming up...")
    for _ in range(3):
        local_uroman.romanize_string(test_text)
        requests.post(REST_ENDPOINT, json={"text": test_text})
    
    # Measure baseline
    print("\n📊 Baseline Performance (single request):")
    
    # Local
    times = []
    for _ in range(20):
        start = time.time()
        local_uroman.romanize_string(test_text)
        times.append(time.time() - start)
    local_baseline_ms = statistics.mean(times) * 1000
    print(f"  Local: {local_baseline_ms:.1f}ms")
    
    # Remote
    times = []
    for _ in range(5):
        start = time.time()
        resp = requests.post(REST_ENDPOINT, json={"text": test_text})
        times.append(time.time() - start)
    remote_baseline_ms = statistics.mean(times) * 1000
    print(f"  Remote: {remote_baseline_ms:.1f}ms")
    
    # Calculate capacities
    print("\n📈 Theoretical Capacity:")
    
    # Local capacity (assuming CPU-bound)
    local_single_thread_rps = 1000 / local_baseline_ms
    local_max_rps = local_single_thread_rps * cpu_count
    print(f"  Local single-thread: {local_single_thread_rps:.0f} req/s")
    print(f"  Local with {cpu_count} cores: {local_max_rps:.0f} req/s")
    
    # Remote capacity
    remote_single_rps = 1000 / remote_baseline_ms
    print(f"  Remote per connection: {remote_single_rps:.1f} req/s")
    print(f"  Remote with 100 connections: {remote_single_rps * 100:.0f} req/s")
    print(f"  Remote max: Unlimited (auto-scales)")
    
    # Real-world scenarios
    print("\n🎯 TIPPING POINTS:")
    print("\nScenario 1: API serving (1 request per user per second)")
    print(f"  Local can handle: up to {int(local_max_rps)} users")
    print(f"  Remote better for: >{int(local_max_rps)} users")
    
    print("\nScenario 2: Batch processing (10 requests per user per second)")
    print(f"  Local can handle: up to {int(local_max_rps/10)} power users")
    print(f"  Remote better for: >{int(local_max_rps/10)} power users")
    
    print("\nScenario 3: Real-time chat (0.1 requests per user per second)")
    print(f"  Local can handle: up to {int(local_max_rps*10)} chat users")
    print(f"  Remote better for: >{int(local_max_rps*10)} chat users")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("=" * 60)
    
    if local_max_rps < 1000:
        threshold_low = 50
        threshold_high = 200
    elif local_max_rps < 5000:
        threshold_low = int(local_max_rps * 0.1)
        threshold_high = int(local_max_rps * 0.5)
    else:
        threshold_low = 500
        threshold_high = 2500
    
    print(f"\n1. LOW TRAFFIC (<{threshold_low} req/s):")
    print("   ✅ Use LOCAL - Lower latency, no network dependency")
    
    print(f"\n2. MEDIUM TRAFFIC ({threshold_low}-{threshold_high} req/s):")
    print("   🤔 Consider your needs:")
    print("   - Need offline? → LOCAL")
    print("   - Need auto-scaling? → REMOTE")
    print("   - Burst traffic? → REMOTE")
    
    print(f"\n3. HIGH TRAFFIC (>{threshold_high} req/s):")
    print("   ✅ Use REMOTE - Better scalability, no CPU bottleneck")
    
    print(f"\n4. VERY HIGH TRAFFIC (>{int(local_max_rps)} req/s):")
    print("   🚨 MUST use REMOTE - Exceeds local capacity")
    
    # Other considerations
    print("\n📌 Other Factors:")
    print("  • Local: {:.1f}ms latency (no network)".format(local_baseline_ms))
    print("  • Remote: {:.1f}ms latency (includes network)".format(remote_baseline_ms))
    print("  • Local: Limited by your {} CPU cores".format(cpu_count))
    print("  • Remote: Scales to thousands of instances")
    print("  • Local: Free (your electricity)")
    print("  • Remote: $0.00001/request (Modal pricing)")

if __name__ == "__main__":
    main()
