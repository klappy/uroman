"""
Test file to demonstrate MCP integration in Cursor

Instructions:
1. Open this file in Cursor
2. Select some code and ask Cursor AI to "romanize the text in this code"
3. Or ask Cursor AI questions like "how do I romanize Chinese text?"

The .cursorrules file tells Cursor AI about the uroman service.
"""

# Test data in various scripts
test_texts = {
    "English": "Hello World",
    "Russian": "Привет мир",
    "Chinese": "你好世界",
    "Arabic": "مرحبا بالعالم",
    "Japanese": "こんにちは世界",
    "Hindi": "नमस्ते दुनिया",
    "Greek": "Γεια σου κόσμε",
    "Hebrew": "שלום עולם",
    "Thai": "สวัสดีชาวโลก",
    "Korean": "안녕하세요 세계"
}

# Example 1: Ask Cursor AI to "romanize all the text values in test_texts"

# Example 2: Ask Cursor AI to "create a function that romanizes the test_texts dictionary"

# Example 3: Select this comment and ask Cursor to romanize it:
# Это комментарий на русском языке. 这是中文评论。 هذا تعليق بالعربية

# Example 4: Ask Cursor AI to "show me how to use the uroman API"

# Example 5: International product names that need romanization
products = [
    {"name": "北京烤鸭", "price": 25.99},
    {"name": "Московский торт", "price": 15.50},
    {"name": "قهوة عربية", "price": 4.99},
    {"name": "寿司セット", "price": 18.75}
]

# Ask Cursor: "romanize the product names and create URL-safe slugs"

# Example 6: Customer names from different countries
customers = [
    "José García",
    "王明",
    "محمد الأحمد", 
    "Владимир Петров",
    "राज शर्मा"
]

# Ask Cursor: "normalize these customer names for a search index"


def test_direct_api():
    """
    Direct API test - you can run this to verify the service works
    """
    import requests
    
    # Test single romanization
    response = requests.post(
        "https://klappy--uroman-service-romanize-endpoint.modal.run",
        json={"text": "Привет мир", "lang_code": "rus"}
    )
    print("Single text result:", response.json())
    
    # Test without language code (auto-detection)
    response = requests.post(
        "https://klappy--uroman-service-romanize-endpoint.modal.run",
        json={"text": "你好世界"}
    )
    print("Auto-detected result:", response.json())


if __name__ == "__main__":
    print("🧪 Cursor MCP Integration Test")
    print("\nThis file demonstrates how to use uroman with Cursor AI.")
    print("\nTry these commands with Cursor AI:")
    print("1. 'Romanize all the text in test_texts'")
    print("2. 'Create a function to romanize product names'")
    print("3. 'Show me how to batch process these customer names'")
    print("\nOr run the direct API test:")
    print("python test_cursor_mcp_integration.py")
    
    # Uncomment to run direct test:
    # test_direct_api()
