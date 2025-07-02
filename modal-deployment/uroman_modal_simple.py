"""
Uroman deployment on Modal.ai - Simplified version
"""

import modal
import sys
from pathlib import Path

# Create our Modal app
app = modal.App("uroman-service-simple")

# Define the container image
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "regex",
        "unicodedata2",
        "fastapi[standard]",
    )
    .add_local_dir("../uroman", "/app/uroman")
)

# Global variable to hold uroman instance
uroman_instance = None

@app.function(image=image, scaledown_window=300)
@modal.fastapi_endpoint(method="POST")
def romanize_endpoint(item: dict) -> dict:
    """
    Simple web endpoint for romanization
    """
    global uroman_instance
    
    # Initialize uroman on first request (lazy loading)
    if uroman_instance is None:
        sys.path.insert(0, '/app')
        from uroman.uroman import Uroman
        uroman_instance = Uroman()
        print("Uroman initialized!")
    
    text = item.get("text", "")
    lang_code = item.get("lang_code", None)
    
    if not text:
        return {"error": "No text provided"}
    
    try:
        romanized = uroman_instance.romanize_string(text, lang_code)
        return {
            "original": text,
            "romanized": romanized,
            "lang_code": lang_code
        }
    except Exception as e:
        return {"error": str(e)}

@app.function(image=image)
def test_romanize(text: str, lang_code: str = None) -> str:
    """
    Simple function for testing
    """
    sys.path.insert(0, '/app')
    from uroman.uroman import Uroman
    uroman = Uroman()
    return uroman.romanize_string(text, lang_code)

@app.local_entrypoint()
def main():
    """
    Test locally
    """
    print("Testing romanization...")
    result = test_romanize.remote("Привет мир", "rus")
    print(f"Result: {result}")
