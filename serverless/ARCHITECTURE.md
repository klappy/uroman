# Architecture Overview

## System Design

The uroman MCP server is designed with serverless constraints in mind, prioritizing fast cold starts, minimal memory usage, and platform portability.

## Core Components

### 1. MCP Server Core (`mcp-server.ts`)

The main MCP server implementation using the Model Context Protocol SDK:

```typescript
class UromanMCPServer {
  private uromanService: UromanService;
  
  constructor() {
    // Lazy initialization for faster cold starts
    this.uromanService = new UromanService();
  }
  
  // MCP tool implementations
  async romanize(params: RomanizeParams): Promise<RomanizeResult>
  async romanizeBatch(params: RomanizeBatchParams): Promise<RomanizeBatchResult>
  async detectScript(params: DetectScriptParams): Promise<DetectScriptResult>
}
```

### 2. Uroman Service Layer (`uroman-service.ts`)

Wrapper around the uroman Python package with optimizations:

```typescript
class UromanService {
  private uromanInstance: Uroman | null = null;
  
  // Lazy loading pattern
  private async getUroman(): Promise<Uroman> {
    if (!this.uromanInstance) {
      this.uromanInstance = await this.loadUroman();
    }
    return this.uromanInstance;
  }
  
  // Singleton pattern for instance reuse
  private async loadUroman(): Promise<Uroman> {
    // Load uroman with optimized data loading
    return new Uroman({
      cache_size: 65536,  // Optimize for serverless memory constraints
      load_log: false     // Reduce startup overhead
    });
  }
}
```

### 3. Platform Adapters

Each serverless platform requires a specific adapter to handle requests:

#### Cloudflare Workers Adapter
```typescript
// adapters/cloudflare.ts
export default {
  async fetch(request: Request): Promise<Response> {
    const mcp = getMCPServerInstance();
    const result = await mcp.handleRequest(request);
    return new Response(JSON.stringify(result));
  }
}
```

#### Netlify Functions Adapter
```typescript
// adapters/netlify.ts
export const handler = async (event, context) => {
  const mcp = getMCPServerInstance();
  const result = await mcp.handleRequest(event);
  return {
    statusCode: 200,
    body: JSON.stringify(result)
  };
}
```

## Design Patterns

### 1. Lazy Loading
- Uroman data is only loaded on first request
- Reduces cold start time significantly
- Trade-off: First request is slower

### 2. Singleton Pattern
- Single uroman instance per function lifetime
- Reused across multiple invocations
- Reduces memory usage and improves performance

### 3. Adapter Pattern
- Platform-specific adapters handle request/response formats
- Core MCP logic remains platform-agnostic
- Easy to add new platform support

### 4. Resource Pooling
- Reuse romanization cache across requests
- Configurable cache size based on platform limits
- Automatic cache eviction when full

## Data Flow

```
1. Client Request → Platform Handler
2. Platform Handler → MCP Adapter
3. MCP Adapter → MCP Server Core
4. MCP Server Core → Uroman Service
5. Uroman Service → Uroman Instance (lazy loaded)
6. Response flows back through the same path
```

## Performance Optimizations

### Cold Start Optimization
- Minimal top-level imports
- Lazy loading of heavy dependencies
- Pre-compiled TypeScript bundles

### Memory Optimization
- Configurable cache sizes
- Efficient data structures
- Garbage collection hints

### Response Time Optimization
- Request-level caching
- Batch processing support
- Streaming responses for large payloads

## Scalability Considerations

### Horizontal Scaling
- Stateless design allows infinite horizontal scaling
- Each instance is independent
- No shared state between instances

### Vertical Scaling
- Memory usage scales with cache size
- CPU usage scales with text complexity
- Configurable limits for both

### Multi-Region Deployment
- Deploy to edge locations (Cloudflare)
- Regional deployments (Netlify, Vercel)
- Latency optimization through geographic distribution

## Security Considerations

### Input Validation
- Text length limits to prevent DoS
- Character encoding validation
- Language code validation

### Rate Limiting
- Platform-level rate limiting
- Optional application-level throttling
- Cost protection mechanisms

### Data Privacy
- No persistent storage of user data
- In-memory caching only
- No logging of sensitive content

## Error Handling

### Graceful Degradation
- Fallback to basic romanization on errors
- Partial results for batch operations
- Clear error messages for debugging

### Retry Logic
- Platform-specific retry mechanisms
- Exponential backoff for transient errors
- Circuit breaker pattern for persistent failures

## Monitoring and Observability

### Metrics
- Cold start duration
- Request latency
- Memory usage
- Cache hit rates

### Logging
- Structured logging for easy parsing
- Log levels based on environment
- Performance profiling in development

### Tracing
- Request ID propagation
- Distributed tracing support
- Performance bottleneck identification
