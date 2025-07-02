## Modal.ai Cloud Deployment

### Quick Start

The uroman service is available as a cloud API via Modal.ai:

**REST API Endpoint**: `https://klappy--uroman-service-romanize-endpoint.modal.run`

**MCP Server Endpoint**: `https://klappy--uroman-service-mcp-endpoint.modal.run`

#### Example Usage

```bash
# Simple REST API call
curl -X POST https://klappy--uroman-service-romanize-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -d '{"text": "Привет мир", "lang_code": "rus"}'

# Response: {"original": "Привет мир", "romanized": "Privet mir", "lang_code": "rus"}
```

### Deploy Your Own Instance

1. Install Modal:
```bash
pip install modal
```

2. Authenticate:
```bash
modal setup
```

3. Deploy:
```bash
cd serverless/deployments/modal
modal deploy deploy.py
```

### Multi-Cloud Architecture

The new `serverless/` directory contains a platform-agnostic architecture that supports:
- Modal.ai (fully deployed) ✅
- AWS Lambda (ready to deploy)
- Google Cloud Functions (compatible)
- Azure Functions (compatible)
- Cloudflare Workers ❌ (not viable - see limitations)

### Performance

- **Local**: ~1ms latency, up to 2,500+ requests/second
- **Remote**: ~250ms latency, unlimited scaling
- **Tipping point**: Remote becomes beneficial at >500 requests/second

See `serverless/` directory for the new multi-cloud deployment architecture.
