# MCP API Reference

## Overview

The uroman MCP server implements the Model Context Protocol, providing tools and resources for universal romanization.

## Base Configuration

```json
{
  "name": "uroman-mcp-server",
  "version": "1.0.0",
  "description": "Universal romanization through Model Context Protocol",
  "protocols": ["mcp/1.0"],
  "capabilities": {
    "tools": true,
    "resources": true,
    "prompts": false,
    "sampling": false
  }
}
```

## Tools

### 1. `romanize`

Converts text in any script to the Latin alphabet.

**Parameters:**
```typescript
{
  "text": {
    "type": "string",
    "description": "Text to romanize",
    "required": true,
    "maxLength": 10000
  },
  "language": {
    "type": "string",
    "description": "ISO 639-3 language code (e.g., 'hin' for Hindi)",
    "required": false,
    "pattern": "^[a-z]{3}$"
  },
  "format": {
    "type": "string",
    "description": "Output format",
    "required": false,
    "enum": ["str", "edges"],
    "default": "str"
  }
}
```

**Response (format: "str"):**
```json
{
  "type": "text",
  "content": "romanized text"
}
```

**Response (format: "edges"):**
```json
{
  "type": "json",
  "content": [
    {
      "start": 0,
      "end": 1,
      "original": "П",
      "romanized": "P",
      "confidence": 1.0
    }
  ]
}
```

**Examples:**
```json
// Request
{
  "tool": "romanize",
  "parameters": {
    "text": "Привет мир",
    "language": "rus"
  }
}

// Response
{
  "type": "text",
  "content": "Privet mir"
}
```

### 2. `romanize_batch`

Efficiently romanizes multiple texts in a single request.

**Parameters:**
```typescript
{
  "texts": {
    "type": "array",
    "description": "Array of texts to romanize",
    "required": true,
    "items": {
      "type": "string",
      "maxLength": 1000
    },
    "maxItems": 100
  },
  "language": {
    "type": "string",
    "description": "ISO 639-3 language code for all texts",
    "required": false,
    "pattern": "^[a-z]{3}$"
  }
}
```

**Response:**
```json
{
  "type": "json",
  "content": {
    "results": [
      {
        "index": 0,
        "original": "नमस्ते",
        "romanized": "namaste",
        "success": true
      },
      {
        "index": 1,
        "original": "مرحبا",
        "romanized": "mrhba",
        "success": true
      }
    ],
    "stats": {
      "total": 2,
      "successful": 2,
      "failed": 0,
      "processingTime": 45
    }
  }
}
```

**Examples:**
```json
// Request
{
  "tool": "romanize_batch",
  "parameters": {
    "texts": ["Hello", "Привет", "你好", "مرحبا"]
  }
}

// Response
{
  "type": "json",
  "content": {
    "results": [
      {"index": 0, "original": "Hello", "romanized": "Hello", "success": true},
      {"index": 1, "original": "Привет", "romanized": "Privet", "success": true},
      {"index": 2, "original": "你好", "romanized": "nihao", "success": true},
      {"index": 3, "original": "مرحبا", "romanized": "mrhba", "success": true}
    ],
    "stats": {
      "total": 4,
      "successful": 4,
      "failed": 0,
      "processingTime": 67
    }
  }
}
```

### 3. `detect_script`

Detects the writing system(s) used in the provided text.

**Parameters:**
```typescript
{
  "text": {
    "type": "string",
    "description": "Text to analyze",
    "required": true,
    "maxLength": 5000
  },
  "detailed": {
    "type": "boolean",
    "description": "Include character-level script information",
    "required": false,
    "default": false
  }
}
```

**Response:**
```json
{
  "type": "json",
  "content": {
    "scripts": [
      {
        "name": "Cyrillic",
        "code": "Cyrl",
        "percentage": 45.5,
        "characterCount": 10
      },
      {
        "name": "Latin",
        "code": "Latn",
        "percentage": 54.5,
        "characterCount": 12
      }
    ],
    "primaryScript": "Latin",
    "mixedScript": true
  }
}
```

**Examples:**
```json
// Request
{
  "tool": "detect_script",
  "parameters": {
    "text": "Hello мир! 世界",
    "detailed": true
  }
}

// Response
{
  "type": "json",
  "content": {
    "scripts": [
      {"name": "Latin", "code": "Latn", "percentage": 50, "characterCount": 6},
      {"name": "Cyrillic", "code": "Cyrl", "percentage": 25, "characterCount": 3},
      {"name": "Han", "code": "Hani", "percentage": 25, "characterCount": 2}
    ],
    "primaryScript": "Latin",
    "mixedScript": true,
    "details": [
      {"char": "H", "script": "Latin"},
      {"char": "м", "script": "Cyrillic"},
      {"char": "世", "script": "Han"}
    ]
  }
}
```

## Resources

### 1. Language Codes

**URI:** `uroman://languages`

**Description:** List of supported ISO 639-3 language codes with their names and script information.

**Response:**
```json
{
  "type": "json",
  "mimeType": "application/json",
  "content": [
    {
      "code": "hin",
      "name": "Hindi",
      "script": "Devanagari",
      "nativeName": "हिन्दी"
    },
    {
      "code": "rus",
      "name": "Russian",
      "script": "Cyrillic",
      "nativeName": "Русский"
    }
  ]
}
```

### 2. Supported Scripts

**URI:** `uroman://scripts`

**Description:** List of all writing systems supported by uroman.

**Response:**
```json
{
  "type": "json",
  "mimeType": "application/json",
  "content": [
    {
      "name": "Arabic",
      "code": "Arab",
      "direction": "rtl",
      "languages": ["ara", "fas", "urd"],
      "characterCount": 1234
    },
    {
      "name": "Devanagari",
      "code": "Deva",
      "direction": "ltr",
      "languages": ["hin", "mar", "nep"],
      "characterCount": 567
    }
  ]
}
```

### 3. Romanization Examples

**URI:** `uroman://examples/{script}`

**Description:** Example romanizations for a specific script.

**Response:**
```json
{
  "type": "json",
  "mimeType": "application/json",
  "content": {
    "script": "Cyrillic",
    "examples": [
      {"original": "Привет", "romanized": "Privet", "language": "Russian"},
      {"original": "Київ", "romanized": "Kyiv", "language": "Ukrainian"}
    ]
  }
}
```

## Error Handling

All tools return errors in a consistent format:

```json
{
  "error": {
    "code": "INVALID_LANGUAGE_CODE",
    "message": "Language code 'xyz' is not a valid ISO 639-3 code",
    "details": {
      "provided": "xyz",
      "suggestion": "Did you mean 'xho' (Xhosa)?"
    }
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_INPUT` | Input validation failed | 400 |
| `TEXT_TOO_LONG` | Input exceeds maximum length | 400 |
| `INVALID_LANGUAGE_CODE` | Unknown language code | 400 |
| `UNSUPPORTED_SCRIPT` | Script not supported | 400 |
| `ROMANIZATION_FAILED` | Internal romanization error | 500 |
| `TIMEOUT` | Operation timed out | 504 |
| `RATE_LIMITED` | Too many requests | 429 |

## Rate Limiting

The MCP server implements rate limiting to prevent abuse:

- **Default limits**: 100 requests per minute
- **Batch operations**: Count as number of items in batch
- **Headers returned**:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Time when limit resets

## Performance Considerations

### Response Times

| Operation | Typical | Maximum |
|-----------|---------|---------|
| Single romanization | 10-50ms | 200ms |
| Batch (10 items) | 50-200ms | 1s |
| Script detection | 5-20ms | 100ms |

### Size Limits

| Parameter | Limit | Notes |
|-----------|-------|-------|
| Single text | 10,000 chars | ~5 pages |
| Batch size | 100 items | Per request |
| Batch item | 1,000 chars | Per item |
| Total batch | 50,000 chars | Combined |

## Client Examples

### JavaScript/TypeScript

```typescript
import { MCPClient } from '@modelcontextprotocol/client';

const client = new MCPClient('https://uroman-mcp.example.com');

// Simple romanization
const result = await client.callTool('romanize', {
  text: 'Здравствуйте',
  language: 'rus'
});
console.log(result.content); // "Zdravstvuite"

// Batch romanization
const batchResult = await client.callTool('romanize_batch', {
  texts: ['Hello', 'Привет', '你好']
});
console.log(batchResult.content.results);

// Get supported languages
const languages = await client.getResource('uroman://languages');
console.log(languages.content);
```

### Python

```python
from mcp_client import MCPClient

client = MCPClient('https://uroman-mcp.example.com')

# Simple romanization
result = client.call_tool('romanize', {
    'text': 'नमस्ते',
    'language': 'hin'
})
print(result['content'])  # "namaste"

# Detect script
script_info = client.call_tool('detect_script', {
    'text': 'Hello мир',
    'detailed': True
})
print(script_info['content']['scripts'])
```

## Versioning

The API follows semantic versioning:

- **Current version**: 1.0.0
- **Version header**: `X-MCP-Version`
- **Backwards compatibility**: Guaranteed for major versions
