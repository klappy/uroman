"""
Uroman deployment on Modal.ai (Updated for Modal 1.0)
"""

import modal
from pathlib import Path
import sys

# Create our Modal app
app = modal.App("uroman-service")

# Define the container image with FastAPI and dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "regex",
        "unicodedata2",
        "fastapi[standard]",  # Required for web endpoints
    )
    .add_local_dir("../uroman", "/app/uroman")  # Updated method name
)

@app.cls(
    image=image,
    gpu=None,
    scaledown_window=300,  # Updated parameter name (was container_idle_timeout)
)
class UromanService:
    @modal.enter()  # Use @modal.enter() instead of __init__
    def setup(self):
        # Import uroman when the container starts
        sys.path.insert(0, '/app')
        from uroman.uroman import Uroman
        self.uroman = Uroman()
        print("Uroman initialized and ready to romanize!")
    
    @modal.method()
    def romanize(self, text: str, lang_code: str = None) -> str:
        """
        Romanize text. It's like Google Translate, but just for the alphabet.
        """
        return self.uroman.romanize_string(text, lang_code)
    
    @modal.fastapi_endpoint(method="POST")  # Updated decorator name
    def romanize_endpoint(self, item: dict) -> dict:
        """
        Web endpoint for romanization. 
        Send JSON with 'text' and optionally 'lang_code'.
        """
        text = item.get("text", "")
        lang_code = item.get("lang_code", None)
        
        if not text:
            return {"error": "No text provided"}
        
        try:
            romanized = self.romanize(text, lang_code)
            return {
                "original": text,
                "romanized": romanized,
                "lang_code": lang_code
            }
        except Exception as e:
            return {"error": str(e)}

@app.local_entrypoint()
def main():
    """
    Test our service locally before deploying.
    """
    service = UromanService()
    
    # Test with some examples
    test_texts = [
        ("Hello world", None),
        ("Привет мир", "rus"),  # Russian
        ("你好世界", "zho"),     # Chinese
        ("مرحبا بالعالم", "ara"), # Arabic
    ]
    
    for text, lang in test_texts:
        result = service.romanize.remote(text, lang)  # Use .remote() for local testing
        print(f"{text} -> {result}")
