# Deployment Guide

## Prerequisites

Before deploying the uroman MCP server, ensure you have:

1. Node.js 18+ installed
2. Git installed
3. A GitHub account (for forking the repository)
4. Account on your chosen serverless platform

## Build Process

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-username/uroman.git
cd uroman/serverless

# Install dependencies
npm install

# Build the project
npm run build
```

### 2. Environment Variables

Create a `.env` file for local development:

```env
# Optional: Set cache size (default: 65536)
UROMAN_CACHE_SIZE=65536

# Optional: Enable debug logging
DEBUG=true

# Platform-specific variables will be added below
```

## Platform-Specific Deployment

### Cloudflare Workers

#### 1. Install Wrangler CLI

```bash
npm install -g wrangler
```

#### 2. Configure wrangler.toml

Create `wrangler.toml` in the project root:

```toml
name = "uroman-mcp-server"
main = "dist/adapters/cloudflare.js"
compatibility_date = "2024-01-01"

[build]
command = "npm run build:cloudflare"

[vars]
UROMAN_CACHE_SIZE = "32768"  # Smaller for Cloudflare's memory limits

# Optional: KV namespace for persistent caching
# [[kv_namespaces]]
# binding = "CACHE"
# id = "your-kv-namespace-id"
```

#### 3. Deploy

```bash
# Login to Cloudflare
wrangler login

# Deploy to production
wrangler deploy

# Get your deployment URL
wrangler tail
```

Your server will be available at: `https://uroman-mcp-server.<your-subdomain>.workers.dev`

### Netlify Functions

#### 1. Install Netlify CLI

```bash
npm install -g netlify-cli
```

#### 2. Configure netlify.toml

Create `netlify.toml` in the project root:

```toml
[build]
  command = "npm run build:netlify"
  functions = "dist/functions"
  publish = "dist"

[functions]
  directory = "dist/functions"
  node_bundler = "esbuild"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/mcp-server/:splat"
  status = 200

[build.environment]
  UROMAN_CACHE_SIZE = "65536"
```

#### 3. Deploy

```bash
# Login to Netlify
netlify login

# Initialize the site
netlify init

# Deploy to production
netlify deploy --prod

# Get your deployment URL
netlify status
```

Your server will be available at: `https://your-site-name.netlify.app/api/`

### Vercel

#### 1. Install Vercel CLI

```bash
npm install -g vercel
```

#### 2. Configure vercel.json

Create `vercel.json` in the project root:

```json
{
  "functions": {
    "api/mcp-server.js": {
      "maxDuration": 10,
      "memory": 1024
    }
  },
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/mcp-server"
    }
  ],
  "env": {
    "UROMAN_CACHE_SIZE": "65536"
  },
  "buildCommand": "npm run build:vercel"
}
```

#### 3. Deploy

```bash
# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Get your deployment URL
vercel ls
```

Your server will be available at: `https://your-project.vercel.app/api/`

### AWS Lambda

#### 1. Install AWS SAM CLI

```bash
# macOS
brew install aws-sam-cli

# Or via pip
pip install aws-sam-cli
```

#### 2. Configure template.yaml

Create `template.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 30
    MemorySize: 512
    Runtime: nodejs18.x
    Environment:
      Variables:
        UROMAN_CACHE_SIZE: 65536

Resources:
  UromanMCPFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: dist/
      Handler: adapters/aws-lambda.handler
      Events:
        Api:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY

Outputs:
  ApiUrl:
    Description: "API Gateway endpoint URL"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"
```

#### 3. Deploy

```bash
# Build the application
sam build

# Deploy (first time - guided)
sam deploy --guided

# Subsequent deployments
sam deploy

# Get your deployment URL
aws cloudformation describe-stacks \
  --stack-name uroman-mcp-server \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

## Local Development

### 1. Start Local Server

```bash
# Run with hot reload
npm run dev

# The server will be available at http://localhost:3000
```

### 2. Test with MCP Inspector

```bash
# In another terminal
npx @modelcontextprotocol/inspector http://localhost:3000
```

### 3. Local Testing with Platform CLIs

Each platform CLI supports local development:

```bash
# Cloudflare
wrangler dev

# Netlify
netlify dev

# Vercel
vercel dev

# AWS
sam local start-api
```

## Configuration Options

### Environment Variables

| Variable | Description | Default | Platforms |
|----------|-------------|---------|-----------|
| `UROMAN_CACHE_SIZE` | Size of romanization cache | 65536 | All |
| `DEBUG` | Enable debug logging | false | All |
| `MAX_TEXT_LENGTH` | Maximum text length | 10000 | All |
| `MAX_BATCH_SIZE` | Maximum batch size | 100 | All |
| `RATE_LIMIT_RPM` | Requests per minute | 100 | All |

### Platform-Specific Settings

#### Cloudflare Workers
- Use smaller cache size (32768) due to memory limits
- Consider KV storage for persistent caching
- Enable Durable Objects for state management

#### Netlify Functions
- Use background functions for large batches
- Enable function bundling for faster cold starts
- Configure CORS headers in netlify.toml

#### Vercel
- Use Edge Runtime for better performance
- Configure regions for global deployment
- Enable ISR for cached responses

#### AWS Lambda
- Use Lambda Layers for dependencies
- Configure API Gateway caching
- Set up CloudWatch alarms

## Monitoring and Logging

### Cloudflare Workers
```bash
# View real-time logs
wrangler tail

# Access analytics
wrangler analytics
```

### Netlify Functions
```bash
# View function logs
netlify functions:log mcp-server

# Access dashboard
netlify open
```

### Vercel
```bash
# View logs
vercel logs

# Access dashboard
vercel dashboard
```

### AWS Lambda
```bash
# View CloudWatch logs
sam logs -n UromanMCPFunction --tail

# Access CloudWatch dashboard
aws logs tail /aws/lambda/uroman-mcp-server
```

## Troubleshooting

### Common Issues

#### 1. Bundle Size Too Large

**Error**: Deployment fails due to size limits

**Solution**:
```bash
# Optimize bundle
npm run build:production

# Check bundle size
npm run analyze
```

#### 2. Memory Limit Exceeded

**Error**: Function runs out of memory

**Solution**:
- Reduce cache size: `UROMAN_CACHE_SIZE=16384`
- Increase memory limit (platform-specific)
- Optimize batch processing

#### 3. Timeout Errors

**Error**: Function execution exceeds time limit

**Solution**:
- Reduce batch sizes
- Implement request streaming
- Use background/async processing

#### 4. Cold Start Performance

**Error**: First request is slow

**Solution**:
- Minimize dependencies
- Use platform-specific optimizations
- Implement warming strategies

### Debug Mode

Enable detailed logging:

```bash
# Set in environment
DEBUG=true

# Or in platform config
UROMAN_DEBUG=true
```

## Security Best Practices

1. **API Keys**: Use platform-specific secret management
2. **CORS**: Configure appropriate CORS headers
3. **Rate Limiting**: Implement request throttling
4. **Input Validation**: Sanitize all inputs
5. **Error Handling**: Don't expose internal errors

## Performance Optimization

### 1. Caching Strategy

```javascript
// Platform-specific caching
if (platform === 'cloudflare') {
  // Use KV storage
  await env.CACHE.put(key, value, { expirationTtl: 3600 });
} else {
  // Use in-memory cache
  cache.set(key, value);
}
```

### 2. Bundle Optimization

```json
// package.json
{
  "scripts": {
    "build:optimize": "esbuild src/index.ts --bundle --minify --tree-shaking=true"
  }
}
```

### 3. Response Compression

Enable platform-specific compression:
- Cloudflare: Automatic
- Netlify: Configure in netlify.toml
- Vercel: Configure in vercel.json
- AWS: Enable in API Gateway

## Rollback Procedures

### Quick Rollback Commands

```bash
# Cloudflare
wrangler rollback

# Netlify
netlify deploy --prod --alias previous

# Vercel
vercel rollback

# AWS
sam deploy --parameter-overrides Version=previous
```

## Next Steps

1. Set up monitoring dashboards
2. Configure alerting
3. Implement CI/CD pipeline
4. Add custom domain
5. Enable analytics
