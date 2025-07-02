"""
Uroman deployment on Modal.ai using multi-cloud architecture
"""

import modal
import sys
from pathlib import Path

# Add serverless to path
serverless_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(serverless_path.parent))

# Create our Modal app
app = modal.App("uroman-service")

# Define the container image
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "regex",
        "unicodedata2",
        "fastapi[standard]",
    )
    .add_local_dir(
        str(serverless_path.parent / "uroman"),
        "/app/uroman"
    )
    .add_local_dir(
        str(serverless_path),
        "/app/serverless"
    )
)

# Global adapter instance (initialized in Modal container)
adapter = None

def get_adapter():
    """Get or create adapter instance"""
    global adapter
    if adapter is None:
        sys.path.insert(0, '/app')
        from serverless.adapters.modal_adapter import ModalAdapter
        adapter = ModalAdapter("/app/uroman")
    return adapter

@app.function(image=image, scaledown_window=300)
@modal.fastapi_endpoint(method="POST")
def romanize_endpoint(item: dict) -> dict:
    """HTTP endpoint for romanization"""
    return get_adapter().handle_http_request(item)

@app.function(image=image, scaledown_window=300)
@modal.fastapi_endpoint(method="POST")
def mcp_endpoint(item: dict) -> dict:
    """MCP endpoint for AI assistants"""
    return get_adapter().handle_mcp_request(item)

@app.function(image=image)
def test_function(text: str = "Привет мир", lang_code: str = "rus") -> dict:
    """Test function for local testing"""
    return get_adapter().handle_http_request({
        "text": text,
        "lang_code": lang_code
    })

@app.local_entrypoint()
def main():
    """Test locally"""
    print("Testing romanization...")
    # Test HTTP endpoint
    result = test_function.remote("Привет мир", "rus")
    print(f"HTTP Result: {result}")
    
    print("\nDeployed endpoints:")
    print(f"  HTTP: https://klappy--uroman-service-romanize-endpoint.modal.run")
    print(f"  MCP:  https://klappy--uroman-service-mcp-endpoint.modal.run")
    
    print("\nTo test the deployed endpoints, run:")
    print('  curl -X POST https://klappy--uroman-service-romanize-endpoint.modal.run \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"text": "Привет мир", "lang_code": "rus"}\'')

if __name__ == "__main__":
    main()
