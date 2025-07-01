# Cloudflare Workers Deployment Guide

Deploy the uroman MCP server to Cloudflare Workers for global edge computing with excellent performance and generous free tier.

## Why Cloudflare Workers?

- **100,000 requests/day** on free tier
- **Global edge network** (200+ locations)
- **Fast cold starts** (<10ms in most cases)
- **10ms CPU time** per request (sufficient for romanization)
- **128MB memory** limit (adequate for uroman)
- **Built-in caching** and analytics

## Prerequisites

1. **Cloudflare Account**
   ```bash
   # Sign up at https://dash.cloudflare.com/sign-up
   ```

2. **Wrangler CLI**
   ```bash
   npm install -g wrangler
   wrangler login
   ```

3. **Node.js Dependencies**
   ```bash
   cd serverless
   npm install
   ```

## Quick Deployment

### 1. Build the Worker

```bash
# Build optimized bundle for Workers runtime
npm run build:cloudflare
```

This creates:
- `dist/cloudflare.js` - Optimized bundle (~500KB)
- `dist/cloudflare-meta.json` - Bundle analysis

### 2. Deploy to Cloudflare

```bash
# Deploy to production
cd deploy/cloudflare
wrangler deploy

# Deploy to staging
wrangler deploy --env staging
```

### 3. Test Deployment

```bash
# Health check
curl https://uroman-mcp-server.your-subdomain.workers.dev/health

# MCP request
curl -X POST https://uroman-mcp-server.your-subdomain.workers.dev \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "romanize",
      "arguments": {
        "text": "こんにちは",
        "language": "jpn"
      }
    },
    "id": 1
  }'
```

## Configuration

### Environment Variables

Configure in `wrangler.toml` or Cloudflare Dashboard:

```toml
[vars]
UROMAN_CACHE_SIZE = "1000"     # LRU cache size
UROMAN_LOG_LEVEL = "info"      # debug, info, warn, error
```

### Custom Domain (Optional)

1. **Add domain to Cloudflare**
2. **Configure route in wrangler.toml**:
   ```toml
   [[route]]
   pattern = "uroman-api.yourdomain.com/*"
   zone_name = "yourdomain.com"
   ```

### KV Storage (Optional)

For persistent caching across invocations:

```bash
# Create KV namespace
wrangler kv:namespace create "UROMAN_CACHE"
wrangler kv:namespace create "UROMAN_CACHE" --preview

# Add to wrangler.toml
[kv_namespaces]
{ binding = "UROMAN_CACHE", id = "your-namespace-id", preview_id = "your-preview-id" }
```

## Performance Optimization

### Bundle Size Analysis

```bash
# Analyze bundle composition
npm run build:cloudflare
cat dist/cloudflare-meta.json | jq '.outputs'
```

### Cold Start Optimization

The adapter implements several optimizations:

1. **Lazy Loading** - uroman module loaded only when needed
2. **Singleton Pattern** - Server instance reused across requests
3. **Minimal Dependencies** - Only essential modules bundled
4. **Tree Shaking** - Unused code eliminated

### Monitoring

```bash
# View logs
wrangler tail

# View analytics
wrangler dev --local-protocol=https
```

## API Usage

### MCP Tools

1. **romanize** - Single text romanization
2. **romanize_batch** - Batch processing (up to 100 texts)
3. **detect_script** - Script detection

### Example Client

```typescript
class UromanMCPClient {
  constructor(private workerUrl: string) {}

  async romanize(text: string, language?: string) {
    const response = await fetch(this.workerUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'tools/call',
        params: {
          name: 'romanize',
          arguments: { text, language }
        },
        id: Date.now()
      })
    });
    
    return response.json();
  }
}

// Usage
const client = new UromanMCPClient('https://uroman-mcp-server.your-subdomain.workers.dev');
const result = await client.romanize('你好', 'zho');
```

## Troubleshooting

### Common Issues

1. **Bundle too large**
   ```bash
   # Check bundle size
   ls -lh dist/cloudflare.js
   
   # Optimize imports in src/adapters/cloudflare.ts
   ```

2. **CPU time exceeded**
   ```bash
   # Check processing time in logs
   wrangler tail
   
   # Reduce batch size or implement streaming
   ```

3. **Memory limit exceeded**
   ```bash
   # Monitor memory usage
   # Reduce cache size in environment variables
   ```

### Debug Mode

```bash
# Local development
wrangler dev --local

# Debug logs
export UROMAN_LOG_LEVEL=debug
npm run build:cloudflare
wrangler dev
```

## Cost Estimation

### Free Tier Limits
- **100,000 requests/day**
- **10ms CPU time/request**
- **128MB memory**

### Paid Tier ($5/month)
- **10 million requests/month**
- **50ms CPU time/request**
- **128MB memory**

### Typical Usage
- **Romanization**: ~2-5ms CPU time
- **Batch (10 texts)**: ~8-15ms CPU time
- **Memory**: ~20-50MB typical usage

## Security

### CORS Configuration

CORS is enabled for all origins by default. To restrict:

```typescript
// In src/adapters/cloudflare.ts
const corsHeaders = {
  'Access-Control-Allow-Origin': 'https://yourdomain.com',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};
```

### Rate Limiting

Implement rate limiting using Cloudflare's built-in features:

```toml
# In wrangler.toml
[env.production.limits]
requests_per_minute = 1000
```

## Next Steps

1. **Monitor Performance** - Use Cloudflare Analytics
2. **Optimize Caching** - Implement KV storage for frequently used texts
3. **Custom Domain** - Set up your own domain for production
4. **CI/CD** - Automate deployments with GitHub Actions

## Support

- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Reference](https://developers.cloudflare.com/workers/wrangler/)
- [uroman MCP Server Issues](https://github.com/your-repo/issues) 