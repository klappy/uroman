# Uroman MCP Server on Modal

This is a Model Context Protocol (MCP) server that provides romanization capabilities to AI assistants.

## What is MCP?

Model Context Protocol (MCP) is a standard that allows AI assistants to interact with external tools and services. Think of it as a universal adapter that lets AI models use your tools.

## Available Tools

### 1. `romanize_text`
Converts a single text from any script to Latin alphabet.

**Parameters:**
- `text` (required): The text to romanize
- `lang_code` (optional): ISO language code (e.g., 'rus', 'ara', 'hin')

**Example:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "romanize_text",
    "arguments": {
      "text": "Привет мир",
      "lang_code": "rus"
    }
  }
}
```

### 2. `romanize_batch`
Romanizes multiple texts at once.

**Parameters:**
- `texts` (required): Array of texts to romanize
- `lang_code` (optional): ISO language code

**Example:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "romanize_batch",
    "arguments": {
      "texts": ["你好", "مرحبا", "नमस्ते"],
      "lang_code": null
    }
  }
}
```

## Deployment

1. Deploy to Modal:
```bash
modal deploy uroman_mcp_modal.py
```

2. Get your MCP endpoint URL (will be shown after deployment)

## Using with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "uroman": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "https://your-mcp-endpoint-url.modal.run",
        "-H", "Content-Type: application/json",
        "-d", "@-"
      ]
    }
  }
}
```

## Using with other AI Assistants

Any AI assistant that supports MCP can use this server. Just point it to:
- Endpoint: `https://your-mcp-endpoint-url.modal.run`
- Method: POST
- Content-Type: application/json

## Testing

Test the MCP server:
```bash
# List available tools
curl -X POST https://your-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'

# Use romanize_text tool
curl -X POST https://your-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "romanize_text",
      "arguments": {
        "text": "Здравствуйте",
        "lang_code": "rus"
      }
    },
    "id": 2
  }'
```

## Why Modal instead of Cloudflare?

- **No JavaScript transpilation**: Pure Python implementation
- **No timeout limits**: Cloudflare Workers timeout after 30 seconds
- **Better for ML workloads**: Modal is designed for AI/ML applications
- **Simpler deployment**: Just `modal deploy` and you're done
