# Using Uroman MCP with Cursor AI Assistant

## Setup

1. **`.cursorrules` file is already created** - This tells Cursor AI about the uroman service
2. **The MCP server is deployed** at `https://klappy--uroman-service-mcp-endpoint.modal.run`

## How to Test in Cursor

### Method 1: Ask Cursor AI Directly

Open any file and ask Cursor AI questions like:

- "How do I romanize Chinese text?"
- "Show me how to convert Arabic text to Latin alphabet"
- "Create a function to romanize international names"

Cursor AI will know about the uroman service and provide code using it.

### Method 2: Use the Test File

1. Open `test_cursor_mcp_integration.py`
2. Select code sections and ask Cursor AI to:
   - "Romanize the text in this dictionary"
   - "Create URL slugs from these product names"
   - "Normalize these customer names for search"

### Method 3: In Your Own Code

When writing code, you can ask Cursor AI:

```python
# Select this and ask: "romanize this text"
user_input = "Здравствуйте, как дела?"

# Or ask: "create a function to romanize user input"
```

## Examples of What Cursor AI Can Do

### 1. Generate Romanization Code

Ask: "Create a function to romanize text"

Cursor will generate:
```python
import requests

def romanize_text(text, lang_code=None):
    response = requests.post(
        "https://klappy--uroman-service-romanize-endpoint.modal.run",
        json={"text": text, "lang_code": lang_code}
    )
    return response.json()["romanized"]
```

### 2. Process Data

Select international data and ask: "Romanize all non-Latin text in this data"

### 3. Create Utilities

Ask: "Create a URL slug generator that handles any language"

## What Makes This Different from Claude Desktop

- **Cursor AI Integration**: The AI assistant in Cursor knows about uroman
- **Code Generation**: Cursor will generate code that uses the API
- **Context Aware**: Works with your selected code
- **No Additional Config**: Just the `.cursorrules` file

## Testing the Integration

1. **Quick Test**: Ask Cursor AI "What is uroman and how do I use it?"
2. **Code Test**: Select non-Latin text and ask "romanize this"
3. **Full Test**: Run `python test_cursor_mcp_integration.py`

## Troubleshooting

If Cursor AI doesn't know about uroman:
1. Make sure `.cursorrules` exists in your project root
2. Reload the Cursor window
3. Try a direct question: "The project has a uroman service at https://klappy--uroman-service-romanize-endpoint.modal.run, how do I use it?"

## Direct API Usage (Without Cursor AI)

You can always use the API directly:

```bash
curl -X POST https://klappy--uroman-service-romanize-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -d '{"text": "你好", "lang_code": "zho"}'
```

## Benefits in Cursor

1. **Auto-complete**: Cursor can suggest romanization when dealing with international text
2. **Refactoring**: Ask Cursor to "add romanization to this function"
3. **Documentation**: Cursor knows to suggest romanization for international projects
4. **Testing**: Generate test cases with romanized expected values
