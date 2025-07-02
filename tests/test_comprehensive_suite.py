#!/usr/bin/env python3
"""
Comprehensive test suite for uroman
Tests local CLI, remote service, and compares performance
"""

import json
import os
import subprocess
import sys
import time
import requests
import statistics
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytest
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
import uroman

# Configuration
MCP_ENDPOINT = "https://klappy--uroman-service-mcp-endpoint.modal.run"
REST_ENDPOINT = "https://klappy--uroman-service-romanize-endpoint.modal.run"

# Test data directory
TEXT_DIR = Path(__file__).parent.parent / "text"

# Language mapping
LANG_MAP = {
    'amh': ('Amharic', 'amh'),
    'ara': ('Arabic', 'ara'),
    'ben': ('Bengali', 'ben'),
    'bod': ('Tibetan', 'bod'),
    'egy': ('Egyptian', 'egy'),
    'ell': ('Greek', 'ell'),
    'fas': ('Persian', 'fas'),
    'heb': ('Hebrew', 'heb'),
    'hin': ('Hindi', 'hin'),
    'jpn': ('Japanese', 'jpn'),
    'kor': ('Korean', 'kor'),
    'mar': ('Marathi', 'mar'),
    'mya': ('Myanmar', 'mya'),
    'nep': ('Nepali', 'nep'),
    'rus': ('Russian', 'rus'),
    'tam': ('Tamil', 'tam'),
    'tha': ('Thai', 'tha'),
    'tlh': ('Klingon', 'tlh'),
    'tur': ('Turkish', 'tur'),
    'tzm': ('Tamazight', 'tzm'),
    'uig': ('Uyghur', 'uig'),
    'zho': ('Chinese', 'zho'),
    'multiple': ('Mixed Scripts', None)
}


class TestUromanLocal:
    """Test local uroman functionality"""
    
    @classmethod
    def setup_class(cls):
        """Initialize uroman instance"""
        cls.uroman = uroman.Uroman()
    
    def test_all_language_files(self):
        """Test romanization of all language files"""
        results = {}
        
        for file_path in sorted(TEXT_DIR.glob("*.txt")):
            lang_code = file_path.stem
            lang_name, iso_code = LANG_MAP.get(lang_code, (lang_code, None))
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()][:5]  # Test first 5 lines
            
            if not lines:
                continue
                
            # Test each line
            lang_results = []
            for text in lines:
                start = time.time()
                romanized = self.uroman.romanize_string(text, iso_code)
                elapsed = time.time() - start
                
                lang_results.append({
                    'text': text[:50] + '...' if len(text) > 50 else text,
                    'romanized': romanized[:50] + '...' if len(romanized) > 50 else romanized,
                    'time': elapsed
                })
            
            results[lang_name] = lang_results
            avg_time = statistics.mean(r['time'] for r in lang_results)
            print(f"✓ {lang_name}: {len(lang_results)} samples, avg {avg_time:.3f}s")
        
        # All languages should be tested
        assert len(results) == len(LANG_MAP)
        return results
    
    def test_edge_cases(self):
        """Test edge cases"""
        test_cases = [
            ("", ""),  # Empty string
            ("   ", "   "),  # Whitespace
            ("123", "123"),  # Numbers
            ("!@#$%", "!@#$%"),  # Special chars
            ("😀🎉", "😀🎉"),  # Emojis
            ("Hello\nWorld", "Hello\nWorld"),  # Newline
            ("Mixed Привет 你好", "Mixed Privet nihao"),  # Mixed scripts
        ]
        
        for input_text, expected in test_cases:
            result = self.uroman.romanize_string(input_text)
            assert result == expected, f"Failed for '{input_text}': got '{result}'"
    
    def test_batch_performance(self):
        """Test batch processing performance"""
        # Collect test texts
        texts = []
        for file_path in TEXT_DIR.glob("*.txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                line = f.readline().strip()
                if line:
                    texts.append(line)
        
        texts = texts[:20]  # Limit to 20 for testing
        
        # Time individual processing
        start = time.time()
        individual_results = [self.uroman.romanize_string(t) for t in texts]
        individual_time = time.time() - start
        
        print(f"\nBatch test: {len(texts)} texts")
        print(f"Individual processing: {individual_time:.2f}s")
        print(f"Average per text: {individual_time/len(texts)*1000:.1f}ms")
        
        return individual_results, individual_time


class TestUromanCLI:
    """Test uroman CLI functionality"""
    
    def test_cli_basic(self):
        """Test basic CLI usage"""
        result = subprocess.run(
            ["python3", "-m", "uroman", "Привет мир"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Privet mir" in result.stdout
    
    def test_cli_with_language(self):
        """Test CLI with language code"""
        result = subprocess.run(
            ["python3", "-m", "uroman", "नमस्ते", "-l", "hin"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "namaste" in result.stdout
    
    def test_cli_file_processing(self):
        """Test CLI file processing"""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello World\n")
            f.write("Привет мир\n")
            f.write("你好世界\n")
            temp_file = f.name
        
        try:
            # Test file input
            result = subprocess.run(
                ["python3", "-m", "uroman", "-i", temp_file],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0
            assert "Hello World" in result.stdout
            assert "Privet mir" in result.stdout
            assert "nihaoshijie" in result.stdout
        finally:
            os.unlink(temp_file)
    
    def test_cli_performance(self):
        """Measure CLI performance"""
        test_texts = [
            "Hello world",
            "Привет мир",
            "你好世界",
            "مرحبا بالعالم",
            "नमस्ते संसार"
        ]
        
        times = []
        for text in test_texts:
            start = time.time()
            subprocess.run(
                ["python3", "-m", "uroman", text],
                capture_output=True,
                text=True
            )
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = statistics.mean(times)
        print(f"\nCLI Performance: avg {avg_time:.3f}s per invocation")
        return times


class TestUromanRemote:
    """Test remote uroman service"""
    
    def test_remote_endpoint(self):
        """Test remote REST endpoint"""
        response = requests.post(REST_ENDPOINT, json={
            "text": "Привет из теста",
            "lang_code": "rus"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['romanized'] == "Privet iz testa"
    
    def test_mcp_endpoint(self):
        """Test MCP endpoint"""
        response = requests.post(MCP_ENDPOINT, json={
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert 'result' in data
        assert len(data['result']['tools']) == 2
    
    def test_remote_all_languages(self):
        """Test remote service with all languages"""
        results = {}
        
        for file_path in sorted(TEXT_DIR.glob("*.txt")):
            lang_code = file_path.stem
            lang_name, iso_code = LANG_MAP.get(lang_code, (lang_code, None))
            
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.readline().strip()
            
            if not text:
                continue
            
            start = time.time()
            response = requests.post(REST_ENDPOINT, json={
                "text": text,
                "lang_code": iso_code
            })
            elapsed = time.time() - start
            
            assert response.status_code == 200
            data = response.json()
            
            results[lang_name] = {
                'text': text[:50] + '...' if len(text) > 50 else text,
                'romanized': data['romanized'][:50] + '...' if len(data['romanized']) > 50 else data['romanized'],
                'time': elapsed
            }
            
            print(f"✓ Remote {lang_name}: {elapsed:.3f}s")
        
        return results


class TestLocalVsRemote:
    """Compare local vs remote performance"""
    
    def __init__(self):
        self.uroman = uroman.Uroman()
    
    def compare_performance(self):
        """Compare local vs remote performance"""
        test_texts = []
        
        # Collect diverse test texts
        for file_path in TEXT_DIR.glob("*.txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.readline().strip()
                if text and len(text) < 200:  # Reasonable length
                    lang_code = file_path.stem
                    iso_code = LANG_MAP.get(lang_code, (None, None))[1]
                    test_texts.append((text, iso_code))
        
        test_texts = test_texts[:10]  # Limit for testing
        
        print("\n📊 Local vs Remote Performance Comparison")
        print("=" * 60)
        
        # Test local
        local_times = []
        for text, lang_code in test_texts:
            start = time.time()
            self.uroman.romanize_string(text, lang_code)
            local_times.append(time.time() - start)
        
        # Test remote
        remote_times = []
        for text, lang_code in test_texts:
            start = time.time()
            requests.post(REST_ENDPOINT, json={
                "text": text,
                "lang_code": lang_code
            })
            remote_times.append(time.time() - start)
        
        # Results
        print(f"Samples tested: {len(test_texts)}")
        print(f"\nLocal Performance:")
        print(f"  Average: {statistics.mean(local_times)*1000:.1f}ms")
        print(f"  Median: {statistics.median(local_times)*1000:.1f}ms")
        print(f"  Min: {min(local_times)*1000:.1f}ms")
        print(f"  Max: {max(local_times)*1000:.1f}ms")
        
        print(f"\nRemote Performance:")
        print(f"  Average: {statistics.mean(remote_times)*1000:.1f}ms")
        print(f"  Median: {statistics.median(remote_times)*1000:.1f}ms")
        print(f"  Min: {min(remote_times)*1000:.1f}ms")
        print(f"  Max: {max(remote_times)*1000:.1f}ms")
        
        print(f"\nRemote Overhead: {(statistics.mean(remote_times) - statistics.mean(local_times))*1000:.1f}ms")
        
        return local_times, remote_times
    
    def stress_test_comparison(self):
        """Stress test both local and remote"""
        print("\n💪 Stress Test Comparison")
        print("=" * 60)
        
        test_text = "Hello Привет 你好 مرحبا नमस्ते"
        duration = 10  # seconds
        
        # Local stress test
        print(f"Running local stress test for {duration}s...")
        local_count = 0
        start = time.time()
        while time.time() - start < duration:
            self.uroman.romanize_string(test_text)
            local_count += 1
        local_rps = local_count / duration
        
        # Remote stress test (with rate limiting)
        print(f"Running remote stress test for {duration}s...")
        remote_count = 0
        start = time.time()
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            while time.time() - start < duration:
                future = executor.submit(requests.post, REST_ENDPOINT, json={"text": test_text})
                futures.append(future)
                remote_count += 1
                time.sleep(0.1)  # Rate limit to avoid overwhelming the service
            
            # Wait for completion
            for future in as_completed(futures):
                pass
        
        remote_rps = remote_count / duration
        
        print(f"\nResults:")
        print(f"  Local: {local_rps:.1f} requests/second")
        print(f"  Remote: {remote_rps:.1f} requests/second")
        print(f"  Local is {local_rps/remote_rps:.1f}x faster")
        
        return local_rps, remote_rps


def run_all_tests():
    """Run all tests and generate report"""
    print("🧪 Comprehensive Uroman Test Suite")
    print("=" * 60)
    
    # Local tests
    print("\n📍 Testing Local Functionality...")
    local_test = TestUromanLocal()
    local_test.setup_class()
    local_results = local_test.test_all_language_files()
    local_test.test_edge_cases()
    batch_results, batch_time = local_test.test_batch_performance()
    
    # CLI tests
    print("\n💻 Testing CLI...")
    cli_test = TestUromanCLI()
    cli_test.test_cli_basic()
    cli_test.test_cli_with_language()
    cli_test.test_cli_file_processing()
    cli_times = cli_test.test_cli_performance()
    
    # Remote tests
    print("\n☁️  Testing Remote Service...")
    remote_test = TestUromanRemote()
    remote_test.test_remote_endpoint()
    remote_test.test_mcp_endpoint()
    remote_results = remote_test.test_remote_all_languages()
    
    # Comparison tests
    print("\n🔄 Comparing Local vs Remote...")
    comparison = TestLocalVsRemote()
    local_times, remote_times = comparison.compare_performance()
    local_rps, remote_rps = comparison.stress_test_comparison()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    
    return {
        'local_results': local_results,
        'remote_results': remote_results,
        'local_times': local_times,
        'remote_times': remote_times,
        'local_rps': local_rps,
        'remote_rps': remote_rps
    }


if __name__ == "__main__":
    # Run with pytest if available, otherwise run directly
    try:
        import pytest
        pytest.main([__file__, "-v", "-s"])
    except ImportError:
        results = run_all_tests()
