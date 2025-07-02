"""
Uroman deployment on Modal.ai
This is like putting your text romanizer in the cloud, but fancier.
"""

import modal
from pathlib import Path
import sys

# Create our Modal app - think of this as our cloud apartment
app = modal.App("uroman-service")

# Define the container image with all our dependencies
# It's like packing a suitcase, but for code
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "regex",
        "unicodedata2",
    )
    .copy_local_dir("../uroman", "/app/uroman")
)

@app.cls(
    image=image,
    gpu=None,  # We don't need GPUs for text processing
    container_idle_timeout=300,  # Keep warm for 5 minutes
)
class UromanService:
    def __init__(self):
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
    
    @modal.web_endpoint(method="POST")
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
    Like a dress rehearsal, but for code.
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
        result = service.romanize(text, lang)
        print(f"{text} -> {result}")
