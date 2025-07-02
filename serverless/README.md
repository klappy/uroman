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
│   ├── modal_adapter.py    # Modal.ai adapter ✅
│   ├── aws_lambda_adapter.py # AWS Lambda adapter ✅
│   └── cloudflare_adapter.py # ⚠️ NOT VIABLE (see below)
│
└── deployments/           # Platform-specific deployments
    ├── modal/            # Modal.ai deployment ✅
    ├── aws/              # AWS Lambda deployment
    └── cloudflare/      # ⚠️ NOT VIABLE (see LIMITATIONS.md)
```

## ⚠️ Platform Compatibility

| Platform | Status | Notes |
|----------|--------|-------|
| Modal.ai | ✅ Fully Working | Best choice - no size limits, full Python |
| AWS Lambda | ✅ Ready | 250MB limit is sufficient |
| Google Cloud Functions | ✅ Compatible | Similar to AWS Lambda |
| Azure Functions | ✅ Compatible | Similar to AWS Lambda |
| **Cloudflare Workers** | ❌ **NOT VIABLE** | See [detailed limitations](deployments/cloudflare/LIMITATIONS.md) |
| Vercel | 🔄 Possible | 50MB limit, needs testing |

### Why Cloudflare Workers Don't Work

After extensive testing, Cloudflare Workers cannot support uroman due to:
- **10MB size limit** (uroman needs 13-15MB minimum)
- **No regex module** (only basic `re` without Unicode support)
- **Limited Python support** (experimental, missing critical features)

**Read the full analysis: [deployments/cloudflare/LIMITATIONS.md](deployments/cloudflare/LIMITATIONS.md)**

## 🎯 Design Principles

1. **Separation of Concerns**: Core logic is completely independent of deployment platform
2. **Adapter Pattern**: Each platform has its own adapter that translates platform-specific events
3. **Unified Interface**: Same API across all platforms
4. **Easy Extension**: Add new platforms by creating a new adapter

## 🚀 Quick Start

### Deploy to Modal.ai (Recommended)

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

## 🔧 Adding a New Platform

Before adding a new platform, verify it supports:
- ✅ At least 15MB deployment size
- ✅ Full Python 3.8+ support
- ✅ The `regex` module (not just `re`)
- ✅ Full Unicode support

Then:

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

## 📊 Performance Comparison

| Platform | Cold Start | Warm Response | Size Limit | Python Support |
|----------|------------|---------------|------------|----------------|
| Modal.ai | 5-10s | <100ms | None | Full Native |
| AWS Lambda | 1-5s | <100ms | 250MB | Full Native |
| Google Cloud | 1-5s | <100ms | 100MB | Full Native |
| ~~Cloudflare~~ | ~~<1s~~ | ~~N/A~~ | ~~10MB~~ | ~~Experimental~~ |

## 🤝 Contributing

To add support for a new platform:

1. **First check platform limitations** (see Cloudflare example)
2. Create an adapter in `serverless/adapters/`
3. Add deployment configuration
4. Include tests
5. Update this README

## 📄 License

Same as uroman project - Apache 2.0
