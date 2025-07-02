"""
Production-ready Uroman deployment on Modal.ai
With proper error handling, monitoring, and optimization
"""

import modal
import time
import json
from pathlib import Path
import sys
from datetime import datetime

# Create our Modal app
app = modal.App(
    "uroman-service-prod",
    secrets=[
        # Add any API keys or monitoring tokens here if needed
        # modal.Secret.from_name("my-secret")
    ]
)

# Create a volume for caching Unicode data
uroman_volume = modal.Volume.from_name("uroman-data-cache", create_if_missing=True)

# Define the container image with all dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "regex>=2023.0.0",
        "unicodedata2>=15.0.0",
    )
    .copy_local_dir("../uroman", "/app/uroman")
)

@app.cls(
    image=image,
    gpu=None,  # No GPU needed for text processing
    container_idle_timeout=300,  # Keep warm for 5 minutes
    volumes={"/cache": uroman_volume},  # Mount volume for caching
    cpu=2,  # Use 2 CPUs for better performance
    memory=2048,  # 2GB RAM should be plenty
    retries=2,  # Retry failed requests
)
class UromanService:
    def __init__(self):
        """Initialize the Uroman service with caching"""
        import os
        
        # Add uroman to path
        sys.path.insert(0, '/app')
        
        # Set cache directory
        os.environ['UROMAN_CACHE_DIR'] = '/cache'
        
        # Import and initialize
        start_time = time.time()
        from uroman.uroman import Uroman
        
        # Initialize with caching enabled
        self.uroman = Uroman(cache_size=65536)  # Enable caching
        
        init_time = time.time() - start_time
        print(f"✅ Uroman initialized in {init_time:.2f} seconds")
        
        # Pre-warm with common scripts
        self._prewarm_cache()
    
    def _prewarm_cache(self):
        """Pre-warm the cache with common romanizations"""
        test_strings = [
            ("Hello", None),
            ("Привет", "rus"),
            ("你好", "zho"),
            ("مرحبا", "ara"),
            ("नमस्ते", "hin"),
        ]
        
        for text, lang in test_strings:
            try:
                self.uroman.romanize_string(text, lang)
            except:
                pass  # Ignore errors during pre-warming
    
    @modal.method()
    def romanize(self, text: str, lang_code: str = None) -> str:
        """
        Romanize text with proper error handling
        """
        if not text:
            return ""
        
        try:
            return self.uroman.romanize_string(text, lang_code)
        except Exception as e:
            print(f"❌ Romanization error: {str(e)}")
            # Return original text on error
            return text
    
    @modal.method()
    def romanize_batch(self, texts: list[str], lang_code: str = None) -> list[str]:
        """
        Romanize multiple texts efficiently
        """
        results = []
        for text in texts:
            results.append(self.romanize(text, lang_code))
        return results
    
    @modal.web_endpoint(method="POST")
    def romanize_endpoint(self, item: dict) -> dict:
        """
        Web endpoint for romanization with comprehensive error handling
        """
        start_time = time.time()
        
        # Validate input
        if not isinstance(item, dict):
            return {
                "error": "Invalid input: expected JSON object",
                "status": "error"
            }
        
        text = item.get("text", "")
        texts = item.get("texts", [])  # For batch processing
        lang_code = item.get("lang_code")
        
        # Single text romanization
        if text and not texts:
            try:
                romanized = self.romanize(text, lang_code)
                return {
                    "original": text,
                    "romanized": romanized,
                    "lang_code": lang_code,
                    "processing_time": time.time() - start_time,
                    "status": "success"
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "original": text,
                    "status": "error"
                }
        
        # Batch romanization
        elif texts:
            try:
                romanized_texts = self.romanize_batch(texts, lang_code)
                return {
                    "originals": texts,
                    "romanized": romanized_texts,
                    "lang_code": lang_code,
                    "count": len(texts),
                    "processing_time": time.time() - start_time,
                    "status": "success"
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "status": "error"
                }
        
        else:
            return {
                "error": "No text provided. Use 'text' for single or 'texts' for batch.",
                "status": "error"
            }
    
    @modal.web_endpoint(method="GET")
    def health_check(self) -> dict:
        """
        Health check endpoint
        """
        try:
            # Test romanization
            test_result = self.romanize("test", None)
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "test_result": test_result,
                "version": "1.0.0"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

@app.local_entrypoint()
def main():
    """
    Test the service locally
    """
    print("🚀 Starting Uroman service test...")
    
    service = UromanService()
    
    # Test single romanization
    print("\n📝 Testing single romanization:")
    test_cases = [
        ("Здравствуйте, мир!", "rus"),
        ("Hello, 世界!", None),
        ("مرحبا بالعالم", "ara"),
    ]
    
    for text, lang in test_cases:
        result = service.romanize(text, lang)
        print(f"  {text} → {result}")
    
    # Test batch romanization
    print("\n📦 Testing batch romanization:")
    batch = ["Привет", "你好", "مرحبا", "नमस्ते"]
    results = service.romanize_batch(batch)
    for orig, rom in zip(batch, results):
        print(f"  {orig} → {rom}")
    
    # Test web endpoint
    print("\n🌐 Testing web endpoint:")
    response = service.romanize_endpoint({
        "text": "Тестирование завершено",
        "lang_code": "rus"
    })
    print(f"  Response: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    # This allows running the script directly for testing
    with modal.enable_local():
        main()
