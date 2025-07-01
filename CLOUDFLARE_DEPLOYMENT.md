# Cloudflare Workers Deployment via GitHub Integration

This guide shows how to set up automated deployments of the uroman MCP server to Cloudflare Workers using GitHub integration.

## 🚀 Quick Setup

### 1. Repository Setup

The repository is already configured with:
- ✅ `wrangler.toml` in root directory
- ✅ GitHub Actions workflow (`.github/workflows/deploy-cloudflare.yml`)
- ✅ Build scripts and dependencies

### 2. Cloudflare API Token Setup

1. **Get your Cloudflare API Token**:
   - Go to [Cloudflare Dashboard](https://dash.cloudflare.com/profile/api-tokens)
   - Click **Create Token**
   - Use **Custom token** template with these permissions:
     ```
     Zone:Zone:Read
     Zone:Zone Settings:Edit
     Account:Cloudflare Workers:Edit
     ```
   - Include your account in **Account Resources**
   - Include all zones in **Zone Resources** (or specific zones)

2. **Add to GitHub Secrets**:
   - Go to your GitHub repository
   - Navigate to **Settings** > **Secrets and variables** > **Actions**
   - Click **New repository secret**
   - Name: `CLOUDFLARE_API_TOKEN`
   - Value: Your API token from step 1

### 3. Deploy Methods

#### Option A: GitHub Actions (Recommended)

**Automatic deployment on push to main/master:**

```bash
git add .
git commit -m "Deploy uroman MCP server to Cloudflare Workers"
git push origin main
```

**Staging deployment on pull requests:**
- Create a pull request
- GitHub Actions will automatically deploy to staging environment
- Test your changes before merging

#### Option B: Manual Deployment via Wrangler CLI

```bash
# Install Wrangler globally
npm install -g wrangler

# Authenticate with Cloudflare
wrangler login

# Deploy to production
wrangler deploy

# Deploy to staging
wrangler deploy --env staging
```

#### Option C: Cloudflare Dashboard Integration

1. **Connect GitHub Repository**:
   - Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
   - Navigate to **Workers & Pages**
   - Click **Create application** > **Pages** > **Connect to Git**
   - Select your GitHub repository
   - Choose **Framework preset**: None
   - **Build command**: `cd serverless && npm ci && npm run build:cloudflare`
   - **Build output directory**: `serverless/dist`
   - **Root directory**: `/` (leave empty)
   - **Install command**: Leave empty (auto-detected)

2. **Environment Variables** (Optional):
   - Add `UROMAN_CACHE_SIZE=1000`
   - Add `UROMAN_LOG_LEVEL=info`

## 🔧 Configuration

### Environment Variables

Set these in Cloudflare Dashboard or `wrangler.toml`:

```toml
[vars]
UROMAN_CACHE_SIZE = "1000"     # LRU cache size (default: 1000)
UROMAN_LOG_LEVEL = "info"      # debug, info, warn, error
```

### Custom Domain (Optional)

1. **Add domain to Cloudflare**
2. **Update wrangler.toml**:
   ```toml
   [[route]]
   pattern = "uroman-api.yourdomain.com/*"
   zone_name = "yourdomain.com"
   ```

### KV Storage (Optional)

For persistent caching:

```bash
# Create KV namespace
wrangler kv:namespace create "UROMAN_CACHE"
wrangler kv:namespace create "UROMAN_CACHE" --preview

# Update wrangler.toml
[kv_namespaces]
{ binding = "UROMAN_CACHE", id = "your-namespace-id", preview_id = "your-preview-id" }
```

## 🧪 Testing Your Deployment

### 1. Health Check

```bash
curl https://uroman-mcp-server.your-subdomain.workers.dev/health
```

Expected response:
```json
{
  "status": "healthy",
  "platform": "cloudflare-workers",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "serviceInitialized": true,
  "cacheStats": {
    "size": 0,
    "maxSize": 1000,
    "hitRate": 0
  }
}
```

### 2. MCP Tools List

```bash
curl -X POST https://uroman-mcp-server.your-subdomain.workers.dev \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

### 3. Romanization Test

```bash
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
    "id": 2
  }'
```

## 📊 Monitoring

### GitHub Actions

Monitor deployments in your repository:
- Go to **Actions** tab
- View deployment logs and status
- Check test results

### Cloudflare Dashboard

Monitor usage and performance:
- **Workers & Pages** > Your worker
- View **Metrics** for requests, errors, CPU time
- Check **Logs** for real-time debugging

### Wrangler CLI

```bash
# View logs in real-time
wrangler tail

# View deployment status
wrangler status

# View analytics
wrangler analytics
```

## 🔍 Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check build locally
   cd serverless
   npm install
   npm run build:cloudflare
   ```

2. **API Token Issues**
   - Verify token permissions in Cloudflare Dashboard
   - Ensure token is correctly set in GitHub Secrets

3. **Import Errors**
   - The `uroman` module is dynamically imported at runtime
   - Ensure Python uroman package is available in Workers environment

4. **Memory/CPU Limits**
   - Monitor usage in Cloudflare Dashboard
   - Adjust cache size if needed
   - Consider upgrading to Workers Paid plan for higher limits

### Debug Mode

Enable debug logging:
```toml
[vars]
UROMAN_LOG_LEVEL = "debug"
```

Then check logs:
```bash
wrangler tail --format=pretty
```

## 🚀 Production Checklist

- [ ] GitHub repository connected
- [ ] Cloudflare API token configured
- [ ] Tests passing in GitHub Actions
- [ ] Health check responding
- [ ] MCP tools working correctly
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up
- [ ] Error alerting configured

## 📈 Performance Optimization

### Bundle Analysis

```bash
cd serverless
npm run build:cloudflare
cat dist/cloudflare-meta.json | jq '.outputs'
```

### Cache Optimization

- Monitor cache hit rates in health check
- Adjust `UROMAN_CACHE_SIZE` based on usage patterns
- Consider KV storage for persistent caching

### Cost Optimization

- **Free Tier**: 100,000 requests/day
- **Paid Tier**: $5/month for 10M requests/month
- Monitor usage in Cloudflare Dashboard

## 🔗 Useful Links

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Reference](https://developers.cloudflare.com/workers/wrangler/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [uroman MCP API Reference](serverless/MCP_API_REFERENCE.md) 