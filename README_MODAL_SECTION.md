## Modal.ai Cloud Deployment

### Quick Start

The uroman service is available as a cloud API via Modal.ai:

**REST API Endpoint**: `https://klappy--uroman-service-simple-romanize-endpoint.modal.run`

**MCP Server Endpoint**: `https://klappy--uroman-mcp-server-mcp-endpoint.modal.run`

#### Example Usage

```bash
# Simple REST API call
curl -X POST https://klappy--uroman-service-simple-romanize-endpoint.modal.run \
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
cd modal-deployment
modal deploy uroman_mcp_modal.py
```

### Performance

- **Local**: ~1ms latency, up to 9,000 requests/second (hardware dependent)
- **Remote**: ~250ms latency, unlimited scaling
- **Tipping point**: Remote becomes beneficial at >500 requests/second

See `modal-deployment/` directory for deployment scripts and documentation.

