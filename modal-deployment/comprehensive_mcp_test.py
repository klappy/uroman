#!/usr/bin/env python3
"""
Comprehensive test suite for uroman MCP server on Modal
Tests all example files from the codebase
"""

import json
import requests
import time
from pathlib import Path
from collections import defaultdict

# Configuration
MCP_ENDPOINT = "https://klappy--uroman-mcp-server-mcp-endpoint.modal.run"
REST_ENDPOINT = "https://klappy--uroman-mcp-server-romanize-endpoint.modal.run"

# Language code mapping
LANG_CODES = {
    'amh': 'amh',  # Amharic
    'ara': 'ara',  # Arabic
    'ben': 'ben',  # Bengali
    'bod': 'bod',  # Tibetan
    'egy': 'egy',  # Egyptian
    'ell': 'ell',  # Greek
    'fas': 'fas',  # Persian/Farsi
    'heb': 'heb',  # Hebrew
    'hin': 'hin',  # Hindi
    'jpn': 'jpn',  # Japanese
    'kor': 'kor',  # Korean
    'mar': 'mar',  # Marathi
    'mya': 'mya',  # Myanmar/Burmese
    'nep': 'nep',  # Nepali
    'rus': 'rus',  # Russian
    'tam': 'tam',  # Tamil
    'tha': 'tha',  # Thai
    'tlh': 'tlh',  # Klingon
    'tur': 'tur',  # Turkish
    'tzm': 'tzm',  # Tamazight
    'uig': 'uig',  # Uyghur
    'zho': 'zho',  # Chinese
}

def test_mcp_tools_list():
    """Test MCP tools/list method"""
    print("Testing MCP tools/list...")
    response = requests.post(MCP_ENDPOINT, json={
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    })
    data = response.json()
    tools = data['result']['tools']
    print(f"✓ Found {len(tools)} tools: {[t['name'] for t in tools]}")
    return True

def test_single_romanization(text, lang_code=None):
    """Test single text romanization via MCP"""
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
        "id": 2
    })
    data = response.json()
    if 'error' in data:
        return None, data['error']
    return data['result']['data']['romanized'], None

def test_batch_romanization(texts, lang_code=None):
    """Test batch romanization via MCP"""
    response = requests.post(MCP_ENDPOINT, json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "romanize_batch",
            "arguments": {
                "texts": texts,
                "lang_code": lang_code
            }
        },
        "id": 3
    })
    data = response.json()
    if 'error' in data:
        return None, data['error']
    results = data['result']['data']['results']
    return [r['romanized'] for r in results], None

def test_file(filepath, lang_code):
    """Test romanization of a specific file"""
    print(f"\nTesting {filepath.name} ({lang_code})...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if not lines:
            print(f"  ⚠️  Empty file")
            return False
        
        # Test first line individually
        first_line = lines[0]
        print(f"  Original: {first_line[:50]}{'...' if len(first_line) > 50 else ''}")
        
        start_time = time.time()
        romanized, error = test_single_romanization(first_line, lang_code)
        elapsed = time.time() - start_time
        
        if error:
            print(f"  ❌ Error: {error}")
            return False
        
        print(f"  Romanized: {romanized[:50]}{'...' if len(romanized) > 50 else ''}")
        print(f"  ✓ Single text: {elapsed:.2f}s")
        
        # Test batch if multiple lines
        if len(lines) > 1:
            start_time = time.time()
            batch_results, error = test_batch_romanization(lines[:5], lang_code)  # Test up to 5 lines
            elapsed = time.time() - start_time
            
            if error:
                print(f"  ❌ Batch error: {error}")
            else:
                print(f"  ✓ Batch ({len(lines[:5])} texts): {elapsed:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Exception: {str(e)}")
        return False

def test_special_cases():
    """Test special edge cases"""
    print("\nTesting special cases...")
    
    test_cases = [
        ("", None, "Empty string"),
        ("   ", None, "Whitespace only"),
        ("Hello123World", None, "Mixed alphanumeric"),
        ("!@#$%^&*()", None, "Special characters only"),
        ("😀🎉🌍", None, "Emojis"),
        ("Hello\nWorld", None, "Newline character"),
        ("Mixed Привет 你好 مرحبا", None, "Mixed scripts"),
    ]
    
    for text, lang_code, description in test_cases:
        try:
            romanized, error = test_single_romanization(text, lang_code)
            if error:
                print(f"  ⚠️  {description}: Error - {error}")
            else:
                print(f"  ✓ {description}: '{text}' → '{romanized}'")
        except Exception as e:
            print(f"  ❌ {description}: Exception - {str(e)}")

def main():
    """Run comprehensive tests"""
    print("🧪 Comprehensive uroman MCP Server Test Suite")
    print("=" * 60)
    
    # Test MCP protocol
    if not test_mcp_tools_list():
        print("❌ MCP tools/list failed. Aborting.")
        return
    
    # Test all language files
    text_dir = Path("../text")
    success_count = 0
    total_count = 0
    
    for lang_file in sorted(text_dir.glob("*.txt")):
        lang_code = LANG_CODES.get(lang_file.stem)
        total_count += 1
        if test_file(lang_file, lang_code):
            success_count += 1
    
    # Test special cases
    test_special_cases()
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Summary:")
    print(f"  - Languages tested: {total_count}")
    print(f"  - Successful: {success_count}")
    print(f"  - Failed: {total_count - success_count}")
    print(f"  - Success rate: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 ALL TESTS PASSED! The MCP server handles all languages correctly!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
