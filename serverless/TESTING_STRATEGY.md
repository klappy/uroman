# Testing Strategy

## Overview

This document outlines the comprehensive testing approach for the uroman MCP server, covering local development, integration testing, and performance validation across multiple serverless platforms.

## Testing Pyramid

```
                    E2E Tests
                   /         \
              Integration Tests
             /                 \
        Component Tests
       /                       \
  Unit Tests              Performance Tests
```

## Test Categories

### 1. Unit Tests

**Scope**: Individual functions and classes
**Framework**: Vitest
**Coverage Target**: 90%+

```typescript
// Example unit tests
describe('UromanService', () => {
  test('should romanize simple text', async () => {
    const service = new UromanService();
    const result = await service.romanize('Привет', 'rus');
    expect(result).toBe('Privet');
  });

  test('should handle empty input', async () => {
    const service = new UromanService();
    const result = await service.romanize('');
    expect(result).toBe('');
  });

  test('should cache results', async () => {
    const service = new UromanService();
    const spy = jest.spyOn(service, 'processRomanization');
    
    await service.romanize('Test');
    await service.romanize('Test');
    
    expect(spy).toHaveBeenCalledTimes(1);
  });
});
```

### 2. Component Tests

**Scope**: MCP tool implementations
**Framework**: Vitest + MCP Test Utils

```typescript
describe('MCP Tools', () => {
  let server: UromanMCPServer;

  beforeEach(() => {
    server = new UromanMCPServer();
  });

  test('romanize tool should handle valid input', async () => {
    const result = await server.handleToolCall('romanize', {
      text: 'नमस्ते',
      language: 'hin'
    });

    expect(result.type).toBe('text');
    expect(result.content).toBe('namaste');
  });

  test('romanize_batch tool should process multiple texts', async () => {
    const result = await server.handleToolCall('romanize_batch', {
      texts: ['Hello', 'Привет', '你好']
    });

    expect(result.type).toBe('json');
    expect(result.content.results).toHaveLength(3);
    expect(result.content.stats.successful).toBe(3);
  });
});
```

### 3. Integration Tests

**Scope**: Full MCP server with platform adapters
**Framework**: Vitest + Supertest

```typescript
describe('Platform Integration', () => {
  describe('Cloudflare Adapter', () => {
    test('should handle HTTP requests', async () => {
      const request = new Request('http://localhost/mcp', {
        method: 'POST',
        body: JSON.stringify({
          method: 'tools/call',
          params: {
            name: 'romanize',
            arguments: { text: 'Test' }
          }
        })
      });

      const response = await cloudflareAdapter.fetch(request);
      expect(response.status).toBe(200);
      
      const result = await response.json();
      expect(result.result).toBeDefined();
    });
  });
});
```

### 4. End-to-End Tests

**Scope**: Full deployment testing
**Framework**: Playwright + Custom MCP Client

```typescript
describe('E2E Deployment Tests', () => {
  const platforms = ['cloudflare', 'netlify', 'vercel'];

  platforms.forEach(platform => {
    describe(`${platform} deployment`, () => {
      test('should respond to health check', async () => {
        const url = getDeploymentUrl(platform);
        const response = await fetch(`${url}/health`);
        expect(response.status).toBe(200);
      });

      test('should handle romanization requests', async () => {
        const client = new MCPClient(getDeploymentUrl(platform));
        const result = await client.callTool('romanize', {
          text: 'Тест',
          language: 'rus'
        });
        expect(result.content).toBe('Test');
      });
    });
  });
});
```

## Local Testing Environment

### 1. Serverless Simulator

Create a local environment that mimics serverless behavior:

```typescript
class ServerlessSimulator {
  private instances = new Map<string, any>();
  
  // Simulate cold starts
  async simulateColdStart(handler: Function): Promise<any> {
    const startTime = Date.now();
    const result = await handler();
    const coldStartTime = Date.now() - startTime;
    
    console.log(`Cold start took ${coldStartTime}ms`);
    return result;
  }
  
  // Simulate memory constraints
  async simulateMemoryLimit(handler: Function, limitMB: number): Promise<any> {
    const initialMemory = process.memoryUsage().heapUsed;
    const result = await handler();
    const finalMemory = process.memoryUsage().heapUsed;
    const usedMB = (finalMemory - initialMemory) / 1024 / 1024;
    
    if (usedMB > limitMB) {
      throw new Error(`Memory limit exceeded: ${usedMB}MB > ${limitMB}MB`);
    }
    
    return result;
  }
  
  // Simulate timeout constraints
  async simulateTimeout(handler: Function, timeoutMs: number): Promise<any> {
    return Promise.race([
      handler(),
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Timeout')), timeoutMs)
      )
    ]);
  }
}
```

### 2. Local Development Server

```typescript
// local-server.ts
import express from 'express';
import { UromanMCPServer } from './src/mcp-server';

const app = express();
const mcpServer = new UromanMCPServer();

app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// MCP endpoint
app.post('/mcp', async (req, res) => {
  try {
    const result = await mcpServer.handleRequest(req.body);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Start server
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Local MCP server running on http://localhost:${port}`);
});
```

### 3. Platform-Specific Local Testing

```bash
# Cloudflare Workers
npm run test:cloudflare:local
wrangler dev --local

# Netlify Functions
npm run test:netlify:local
netlify dev

# Vercel
npm run test:vercel:local
vercel dev

# AWS Lambda
npm run test:aws:local
sam local start-api
```

## Performance Testing

### 1. Load Testing

```typescript
// load-test.ts
import { check } from 'k6';
import http from 'k6/http';

export let options = {
  stages: [
    { duration: '2m', target: 10 },   // Ramp up
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
};

export default function() {
  const payload = JSON.stringify({
    method: 'tools/call',
    params: {
      name: 'romanize',
      arguments: { text: 'Это тест производительности' }
    }
  });

  const response = http.post('https://your-deployment.com/mcp', payload, {
    headers: { 'Content-Type': 'application/json' },
  });

  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
```

### 2. Memory Profiling

```typescript
// memory-profile.ts
import { memoryUsage } from 'process';
import { UromanService } from './src/uroman-service';

async function profileMemory() {
  const service = new UromanService();
  const measurements = [];

  for (let i = 0; i < 1000; i++) {
    const before = memoryUsage();
    
    await service.romanize(`Test text ${i}`);
    
    const after = memoryUsage();
    measurements.push({
      iteration: i,
      heapUsed: after.heapUsed - before.heapUsed,
      heapTotal: after.heapTotal - before.heapTotal
    });
  }

  // Analyze memory patterns
  const avgHeapUsed = measurements.reduce((sum, m) => sum + m.heapUsed, 0) / measurements.length;
  console.log(`Average heap used per request: ${avgHeapUsed / 1024} KB`);
}
```

### 3. Cold Start Analysis

```typescript
// cold-start-test.ts
class ColdStartTester {
  async measureColdStart(platform: string): Promise<number> {
    // Simulate fresh instance
    delete require.cache[require.resolve('./src/mcp-server')];
    
    const startTime = Date.now();
    const { UromanMCPServer } = await import('./src/mcp-server');
    const server = new UromanMCPServer();
    await server.initialize();
    const endTime = Date.now();
    
    return endTime - startTime;
  }

  async runColdStartBenchmark(): Promise<void> {
    const platforms = ['cloudflare', 'netlify', 'vercel', 'aws'];
    
    for (const platform of platforms) {
      const times = [];
      
      for (let i = 0; i < 10; i++) {
        const time = await this.measureColdStart(platform);
        times.push(time);
      }
      
      const avg = times.reduce((sum, time) => sum + time, 0) / times.length;
      const min = Math.min(...times);
      const max = Math.max(...times);
      
      console.log(`${platform}: avg=${avg}ms, min=${min}ms, max=${max}ms`);
    }
  }
}
```

## Test Data Sets

### 1. Romanization Test Cases

```typescript
export const testCases = [
  // Basic cases
  { input: 'Hello', language: null, expected: 'Hello' },
  { input: 'Привет', language: 'rus', expected: 'Privet' },
  { input: 'नमस्ते', language: 'hin', expected: 'namaste' },
  
  // Edge cases
  { input: '', language: null, expected: '' },
  { input: '   ', language: null, expected: '   ' },
  { input: '123', language: null, expected: '123' },
  
  // Mixed scripts
  { input: 'Hello мир', language: null, expected: 'Hello mir' },
  { input: 'Test 测试', language: null, expected: 'Test ceshi' },
  
  // Long text
  { input: 'А'.repeat(1000), language: 'rus', expected: 'A'.repeat(1000) },
  
  // Special characters
  { input: 'Café', language: 'fra', expected: 'Cafe' },
  { input: '¿Cómo?', language: 'spa', expected: 'Como?' },
  
  // Numbers in various scripts
  { input: '१२३', language: 'hin', expected: '123' },
  { input: '٩٨٧', language: 'ara', expected: '987' },
];
```

### 2. Performance Test Data

```typescript
export const performanceTestData = {
  small: 'Test',
  medium: 'This is a medium length text for testing performance'.repeat(10),
  large: 'Large text for performance testing '.repeat(1000),
  unicode: '🌍🌎🌏 Unicode test with emojis and symbols ∑∆∇',
  mixed: 'English Русский 中文 العربية हिंदी',
};
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:unit
      - run: npm run test:coverage

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - run: npm run test:integration

  e2e-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    strategy:
      matrix:
        platform: [cloudflare, netlify, vercel]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build:${{ matrix.platform }}
      - run: npm run test:e2e:${{ matrix.platform }}
```

## Test Commands

```json
{
  "scripts": {
    "test": "vitest",
    "test:unit": "vitest run src/**/*.test.ts",
    "test:integration": "vitest run tests/integration/**/*.test.ts",
    "test:e2e": "vitest run tests/e2e/**/*.test.ts",
    "test:performance": "node tests/performance/load-test.js",
    "test:coverage": "vitest run --coverage",
    "test:watch": "vitest --watch",
    "test:cloudflare": "wrangler dev --test",
    "test:netlify": "netlify dev --test",
    "test:vercel": "vercel dev --test",
    "test:aws": "sam local start-api --test"
  }
}
```

## Quality Gates

Before deployment, all tests must pass:

- [ ] Unit test coverage > 90%
- [ ] All integration tests pass
- [ ] E2E tests pass on target platform
- [ ] Performance benchmarks meet targets:
  - Cold start < 500ms
  - Response time < 100ms (median)
  - Memory usage < platform limit
- [ ] No security vulnerabilities
- [ ] Bundle size < platform limit

## Debugging Failed Tests

### Common Issues and Solutions

1. **Memory limit exceeded**
   - Reduce cache size
   - Optimize data loading
   - Use streaming for large responses

2. **Timeout errors**
   - Optimize romanization pipeline
   - Implement request batching
   - Use async processing

3. **Platform-specific failures**
   - Check platform constraints
   - Verify adapter implementation
   - Test with platform CLI locally

### Debug Commands

```bash
# Run tests with debug output
DEBUG=true npm test

# Profile memory usage
npm run test:memory-profile

# Analyze bundle size
npm run analyze

# Test specific platform
npm run test:platform:cloudflare -- --verbose
```
