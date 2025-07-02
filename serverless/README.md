# Uroman Serverless - Multi-Cloud Architecture

Deploy uroman (universal romanizer) to any serverless platform using our unified architecture.

## 🏗️ Architecture Overview

```
serverless/
├── core/                    # Platform-agnostic business logic
│   ├── romanizer_service.py # Core romanization service
│   ├── handler.py          # HTTP request handler
│   └── mcp_handler.py      # MCP protocol handler
│
├── adapters/               # Platform-specific adapters
│   ├── base_adapter.py     # Abstract base class
│   ├── modal_adapter.py    # Modal.ai adapter
│   ├── aws_lambda_adapter.py # AWS Lambda adapter
│   └── (more coming...)    # Cloudflare, Vercel, etc.
│
└── deployments/           # Platform-specific deployments
    ├── modal/            # Modal.ai deployment
    ├── aws/              # AWS Lambda deployment
    └── (more coming...)  # Other platforms
```

## 🎯 Design Principles

1. **Separation of Concerns**: Core logic is completely independent of deployment platform
2. **Adapter Pattern**: Each platform has its own adapter that translates platform-specific events
3. **Unified Interface**: Same API across all platforms
4. **Easy Extension**: Add new platforms by creating a new adapter

## 🚀 Quick Start

### Deploy to Modal.ai

```bash
cd serverless/deployments/modal
modal deploy deploy.py
```

### Deploy to AWS Lambda

```bash
cd serverless/deployments/aws
sam build
sam deploy --guided
```

### Deploy to Cloudflare Workers

```bash
cd serverless/deployments/cloudflare
wrangler deploy
```

## 🔧 Adding a New Platform

1. Create a new adapter in `serverless/adapters/`:

```python
from .base_adapter import ServerlessAdapter

class YourPlatformAdapter(ServerlessAdapter):
    def handle_http_request(self, event, context):
        # Parse platform-specific event
        body = self.parse_your_platform_body(event)
        
        # Use unified handler
        result = self.handler.handle_request(body)
        
        # Return platform-specific response
        return self.create_http_response(200, result)
```

2. Create deployment configuration in `serverless/deployments/your-platform/`

3. Add tests in `serverless/tests/`

## 📡 API Reference

All platforms expose the same API:

### Single Text Romanization
```json
POST /romanize
{
  "text": "Привет мир",
  "lang_code": "rus"
}
```

### Batch Romanization
```json
POST /romanize
{
  "texts": ["Hello", "Привет", "你好"],
  "lang_code": null
}
```

### MCP Protocol (for AI assistants)
```json
POST /mcp
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}
```

## 🧪 Testing

Run tests for all adapters:

```bash
cd serverless
python -m pytest tests/ -v
```

## 📊 Performance

- **Cold Start**: Varies by platform (Modal: 5-10s, AWS: 1-5s, Cloudflare: <1s)
- **Warm Response**: <100ms across all platforms
- **Memory Usage**: ~200MB (configurable per platform)

## 🤝 Contributing

To add support for a new platform:

1. Create an adapter in `serverless/adapters/`
2. Add deployment configuration
3. Include tests
4. Update this README

## 📄 License

Same as uroman project - Apache 2.0
