# Testing the Uroman MCP Server in Cursor

## What is MCP?

MCP (Model Context Protocol) allows AI assistants like Claude to use external tools. The uroman MCP server lets AI assistants romanize text in any script.

## Quick Test in Cursor

### 1. Run the Test Script

Open `test_mcp_in_cursor.py` in Cursor and run it:

```bash
python test_mcp_in_cursor.py
```

This will test:
- Listing available tools
- Single text romanization
- Batch romanization

### 2. Use the Client Class

Open `cursor_mcp_example.py` for a complete example of how to integrate uroman into your projects:

```python
from cursor_mcp_example import UromanMCPClient

# Create client
client = UromanMCPClient()

# Romanize any text
result = client.romanize("Привет мир")
print(result)  # "Privet mir"
```

## Direct API Testing

### Test with curl

```bash
# List available tools
curl -X POST https://klappy--uroman-service-mcp-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'

# Romanize text
curl -X POST https://klappy--uroman-service-mcp-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "romanize_text",
      "arguments": {
        "text": "你好世界",
        "lang_code": "zho"
      }
    },
    "id": 2
  }'
```

## Configure Claude Desktop

To use uroman in Claude Desktop, add this to your config file:

**Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "uroman": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "https://klappy--uroman-service-mcp-endpoint.modal.run",
        "-H", "Content-Type: application/json",
        "-d", "@-"
      ]
    }
  }
}
```

Then restart Claude Desktop and you can ask it to romanize text!

## Use Cases in Cursor

### 1. International Data Processing

```python
# Process international customer names
customer_names = ["王明", "José García", "محمد علي", "Владимир"]
romanized = client.romanize_batch(customer_names)
# ['wangming', 'José García', 'mhmd ly', 'Vladimir']
```

### 2. Search Normalization

```python
# Normalize search queries from different scripts
def normalize_search(query: str) -> str:
    return client.romanize(query.lower())

# All these will match:
normalize_search("москва")  # "moskva"
normalize_search("Москва")  # "moskva"
normalize_search("МОСКВА")  # "moskva"
```

### 3. URL Slug Generation

```python
# Generate URL-safe slugs from any language
def create_slug(title: str) -> str:
    romanized = client.romanize(title)
    return romanized.lower().replace(' ', '-')

create_slug("北京欢迎你")  # "beijinghuanyingni"
create_slug("مرحبا بالعالم")  # "mrhba-blaalm"
```

## Troubleshooting

### Connection Error
If you get connection errors, check:
1. Internet connection
2. The endpoint URL is correct
3. Modal service is deployed (it auto-scales, so first request may be slow)

### Slow First Request
The first request after idle time may take 5-10 seconds (cold start). Subsequent requests are <200ms.

### Rate Limiting
The service auto-scales, but be reasonable with batch sizes (recommended: <100 texts per batch).

## Available Language Codes

Common language codes for better romanization:
- `ara` - Arabic
- `zho` - Chinese
- `rus` - Russian
- `hin` - Hindi
- `jpn` - Japanese
- `kor` - Korean
- `heb` - Hebrew
- `tha` - Thai

Pass `None` for automatic detection.

## Support

- **Issues**: https://github.com/klappy/uroman/issues
- **Endpoints**:
  - MCP: https://klappy--uroman-service-mcp-endpoint.modal.run
  - REST: https://klappy--uroman-service-romanize-endpoint.modal.run
