# Uroman Modal.ai Deployment Guide

## Quick Start (5 minutes)

1. **Install Modal**
   ```bash
   pip install modal
   ```

2. **Authenticate with Modal**
   ```bash
   modal setup
   ```
   This will open a browser to create/login to your Modal account.

3. **Choose Your Deployment**

   **Option A: Simple REST API**
   ```bash
   cd modal-deployment
   modal deploy uroman_modal_simple.py
   ```

   **Option B: MCP Server (for AI assistants)**
   ```bash
   cd modal-deployment
   modal deploy uroman_mcp_modal.py
   ```

   **Option C: Production (with monitoring)**
   ```bash
   cd modal-deployment
   modal deploy uroman_modal_production.py
   ```

## What You Get

After deployment, Modal will give you URLs like:
- `https://your-username--uroman-service-simple-romanize-endpoint.modal.run` (Simple API)
- `https://your-username--uroman-mcp-server-mcp-endpoint.modal.run` (MCP Server)
- `https://your-username--uroman-service-prod-romanize-endpoint.modal.run` (Production)

## Example API Usage

### Single Text
```bash
curl -X POST https://your-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Привет мир",
    "lang_code": "rus"
  }'
```

### Batch Processing
```bash
curl -X POST https://your-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Привет", "你好", "مرحبا"],
    "lang_code": null
  }'
```

## Monitoring

Check the health endpoint (production deployment only):
```bash
curl https://your-health-endpoint.modal.run
```

View logs in Modal dashboard:
```bash
modal app logs uroman-service-prod
```

## Cost Optimization

- The service auto-scales to zero when not in use
- Stays warm for 5 minutes after last request
- First request after cold start: ~5-10 seconds
- Subsequent requests: <100ms

## Comparison: Modal vs Other Platforms

| Feature | Modal | AWS Lambda | Cloudflare Workers |
|---------|-------|------------|-------------------|
| Timeout | No limit | 15 minutes | 30 seconds |
| Memory | Up to 336GB | 10GB | 128MB |
| Cold Start | 5-10s | 1-5s | <1s |
| Python Support | Native | Layers | Via Pyodide |
| Cost | Pay per second | Pay per request | Pay per request |
| Best For | ML/AI workloads | General compute | Edge computing |

## Troubleshooting

1. **Import errors**: Make sure uroman directory is at `../uroman` relative to modal-deployment
2. **Slow cold starts**: This is normal - uroman loads a lot of Unicode data
3. **Out of memory**: Unlikely, but increase memory in the @app.cls decorator if needed

## Next Steps

1. Add authentication (Modal supports secrets)
2. Set up monitoring/alerting
3. Create a simple web UI
4. Add caching for frequently requested texts
