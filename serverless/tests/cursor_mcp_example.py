"""
Example: Using uroman MCP server in your Cursor projects

This shows how to integrate the deployed uroman service into your applications.
"""

import requests
import json
from typing import List, Optional, Dict, Any

class UromanMCPClient:
    """Client for interacting with the uroman MCP server"""
    
    def __init__(self, endpoint: str = "https://klappy--uroman-service-mcp-endpoint.modal.run"):
        self.endpoint = endpoint
        self._request_id = 0
    
    def _make_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        self._request_id += 1
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self._request_id
        }
        
        if params:
            payload["params"] = params
        
        response = requests.post(self.endpoint, json=payload)
        response.raise_for_status()
        return response.json()
    
    def romanize(self, text: str, lang_code: Optional[str] = None) -> str:
        """Romanize a single text"""
        result = self._make_request("tools/call", {
            "name": "romanize_text",
            "arguments": {
                "text": text,
                "lang_code": lang_code
            }
        })
        
        if "error" in result:
            raise Exception(f"MCP Error: {result['error']}")
        
        return result["result"]["data"]["romanized"]
    
    def romanize_batch(self, texts: List[str], lang_code: Optional[str] = None) -> List[str]:
        """Romanize multiple texts at once"""
        result = self._make_request("tools/call", {
            "name": "romanize_batch",
            "arguments": {
                "texts": texts,
                "lang_code": lang_code
            }
        })
        
        if "error" in result:
            raise Exception(f"MCP Error: {result['error']}")
        
        return result["result"]["data"]["romanized"]


# Example usage in Cursor
def main():
    # Create client
    client = UromanMCPClient()
    
    # Example 1: Romanize different scripts
    print("🌍 Romanizing text from different scripts:\n")
    
    examples = [
        ("English", "Hello World", None),
        ("Russian", "Привет мир", "rus"),
        ("Chinese", "你好世界", "zho"),
        ("Arabic", "مرحبا بالعالم", "ara"),
        ("Hindi", "नमस्ते दुनिया", "hin"),
        ("Japanese", "こんにちは世界", "jpn"),
        ("Mixed", "Hello мир 世界", None)
    ]
    
    for name, text, lang_code in examples:
        romanized = client.romanize(text, lang_code)
        print(f"{name:10} {text:20} → {romanized}")
    
    # Example 2: Batch processing
    print("\n📦 Batch processing example:\n")
    
    texts = [
        "The quick brown fox",
        "Быстрая коричневая лиса",
        "敏捷的棕色狐狸",
        "الثعلب البني السريع"
    ]
    
    romanized_batch = client.romanize_batch(texts)
    for original, romanized in zip(texts, romanized_batch):
        print(f"{original:30} → {romanized}")
    
    # Example 3: Processing a document
    print("\n📄 Document processing example:\n")
    
    document = """
    Welcome to our international conference!
    Добро пожаловать на нашу международную конференцию!
    欢迎参加我们的国际会议！
    مرحبا بكم في مؤتمرنا الدولي!
    """
    
    lines = [line.strip() for line in document.strip().split('\n') if line.strip()]
    romanized_lines = client.romanize_batch(lines)
    
    print("Original document:")
    print(document)
    print("\nRomanized version:")
    for line in romanized_lines:
        print(line)


if __name__ == "__main__":
    main()
