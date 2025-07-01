# Performance Optimization Guide

## Overview

This guide covers performance optimization strategies for the uroman MCP server across different serverless platforms, focusing on cold start times, memory usage, and response latency.

## Performance Targets

### Baseline Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cold Start | < 500ms | Time to first response |
| Response Time | < 100ms | P95 for typical requests |
| Memory Usage | < 128MB | Peak memory consumption |
| Bundle Size | < 10MB | Compressed deployment package |
| Cache Hit Rate | > 80% | For repeated romanizations |

### Platform-Specific Targets

| Platform | Cold Start | Memory Limit | Bundle Limit |
|----------|------------|--------------|--------------|
| Cloudflare Workers | < 200ms | 128MB | 1MB (uncompressed) |
| Netlify Functions | < 800ms | 1024MB | 50MB |
| Vercel | < 400ms | 1024MB | 50MB |
| AWS Lambda | < 1000ms | 3008MB | 250MB |

## Cold Start Optimization

### 1. Lazy Loading Strategy

```typescript
class UromanService {
  private static instance: Uroman | null = null;
  private static initPromise: Promise<Uroman> | null = null;

  static async getInstance(): Promise<Uroman> {
    if (this.instance) {
      return this.instance;
    }

    if (this.initPromise) {
      return this.initPromise;
    }

    this.initPromise = this.initializeUroman();
    this.instance = await this.initPromise;
    this.initPromise = null;
    
    return this.instance;
  }

  private static async initializeUroman(): Promise<Uroman> {
    // Lazy load uroman only when needed
    const startTime = Date.now();
    
    const uroman = new (await import('uroman')).Uroman({
      cache_size: process.env.UROMAN_CACHE_SIZE || 32768,
      load_log: false  // Disable logging for faster startup
    });
    
    const loadTime = Date.now() - startTime;
    console.log(`Uroman initialized in ${loadTime}ms`);
    
    return uroman;
  }
}
```

### 2. Minimize Top-Level Imports

```typescript
// ❌ Slow: Loads everything at module level
import { Uroman } from 'uroman';
import * as fs from 'fs';
import * as path from 'path';

// ✅ Fast: Only import what's needed
export async function handler(event: any) {
  // Dynamic imports inside handler
  const { processRequest } = await import('./request-processor');
  return processRequest(event);
}
```

### 3. Pre-compiled Bundles

```json
{
  "scripts": {
    "build:production": "esbuild src/index.ts --bundle --minify --target=es2022 --platform=node --outfile=dist/index.js",
    "build:cloudflare": "esbuild src/adapters/cloudflare.ts --bundle --minify --format=esm --target=es2022 --outfile=dist/cloudflare.js"
  }
}
```

## Memory Optimization

### 1. Configurable Cache Sizes

```typescript
class RomanizationCache {
  private cache = new Map<string, string>();
  private maxSize: number;

  constructor() {
    // Platform-specific cache sizing
    this.maxSize = this.getOptimalCacheSize();
  }

  private getOptimalCacheSize(): number {
    const platform = process.env.PLATFORM;
    const memoryLimit = process.env.MEMORY_LIMIT_MB;

    switch (platform) {
      case 'cloudflare':
        return 1000;  // Small cache for 128MB limit
      case 'netlify':
      case 'vercel':
        return 10000; // Larger cache for 1GB limit
      case 'aws':
        return 50000; // Largest cache for 3GB limit
      default:
        return parseInt(memoryLimit) > 512 ? 10000 : 1000;
    }
  }

  set(key: string, value: string): void {
    if (this.cache.size >= this.maxSize) {
      // LRU eviction
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }
}
```

### 2. Memory Monitoring

```typescript
class MemoryMonitor {
  private static logMemoryUsage(operation: string): void {
    const usage = process.memoryUsage();
    const usageMB = {
      rss: Math.round(usage.rss / 1024 / 1024),
      heapTotal: Math.round(usage.heapTotal / 1024 / 1024),
      heapUsed: Math.round(usage.heapUsed / 1024 / 1024),
      external: Math.round(usage.external / 1024 / 1024)
    };
    
    console.log(`Memory usage after ${operation}:`, usageMB);
    
    // Alert if approaching limits
    const memoryLimitMB = parseInt(process.env.MEMORY_LIMIT_MB || '128');
    if (usageMB.rss > memoryLimitMB * 0.8) {
      console.warn(`Memory usage high: ${usageMB.rss}MB/${memoryLimitMB}MB`);
    }
  }

  static async withMemoryTracking<T>(
    operation: string,
    fn: () => Promise<T>
  ): Promise<T> {
    this.logMemoryUsage(`before ${operation}`);
    const result = await fn();
    this.logMemoryUsage(`after ${operation}`);
    return result;
  }
}
```

### 3. Garbage Collection Hints

```typescript
class ResourceManager {
  private static forceGarbageCollection(): void {
    if (global.gc) {
      global.gc();
    }
  }

  static async cleanupAfterBatch(): Promise<void> {
    // Clear temporary caches
    this.clearTempCaches();
    
    // Force GC if available
    this.forceGarbageCollection();
    
    // Small delay to allow cleanup
    await new Promise(resolve => setTimeout(resolve, 10));
  }
}
```

## Response Time Optimization

### 1. Request-Level Caching

```typescript
class RequestCache {
  private cache = new Map<string, { result: any; timestamp: number }>();
  private ttl = 5 * 60 * 1000; // 5 minutes

  generateKey(text: string, language?: string): string {
    return `${text}:${language || 'auto'}`;
  }

  get(key: string): any | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() - entry.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.result;
  }

  set(key: string, result: any): void {
    this.cache.set(key, {
      result,
      timestamp: Date.now()
    });
  }
}
```

### 2. Batch Processing Optimization

```typescript
class BatchProcessor {
  async processBatch(texts: string[], language?: string): Promise<BatchResult> {
    const results: RomanizationResult[] = [];
    const errors: BatchError[] = [];
    
    // Process in chunks to avoid memory spikes
    const chunkSize = this.getOptimalChunkSize();
    
    for (let i = 0; i < texts.length; i += chunkSize) {
      const chunk = texts.slice(i, i + chunkSize);
      const chunkResults = await this.processChunk(chunk, language);
      
      results.push(...chunkResults.results);
      errors.push(...chunkResults.errors);
      
      // Yield control between chunks
      await new Promise(resolve => setImmediate(resolve));
    }

    return { results, errors };
  }

  private getOptimalChunkSize(): number {
    const platform = process.env.PLATFORM;
    const memoryLimit = parseInt(process.env.MEMORY_LIMIT_MB || '128');
    
    if (memoryLimit < 256) return 10;  // Conservative for low memory
    if (memoryLimit < 512) return 25;  // Moderate chunks
    return 50; // Larger chunks for high memory
  }
}
```

### 3. Streaming Responses

```typescript
class StreamingProcessor {
  async processWithStreaming(
    texts: string[],
    onProgress: (result: RomanizationResult) => void
  ): Promise<void> {
    for (const [index, text] of texts.entries()) {
      try {
        const romanized = await this.romanizeText(text);
        onProgress({
          index,
          original: text,
          romanized,
          success: true
        });
      } catch (error) {
        onProgress({
          index,
          original: text,
          romanized: '',
          success: false,
          error: error.message
        });
      }
      
      // Yield control after each item
      await new Promise(resolve => setImmediate(resolve));
    }
  }
}
```

## Bundle Size Optimization

### 1. Tree Shaking

```typescript
// ❌ Imports entire library
import * as uroman from 'uroman';

// ✅ Import only what's needed
import { Uroman, RomFormat } from 'uroman';

// ✅ Dynamic imports for optional features
async function getAdvancedFeatures() {
  const { AdvancedRomanizer } = await import('./advanced-features');
  return new AdvancedRomanizer();
}
```

### 2. Platform-Specific Builds

```javascript
// webpack.config.js
const config = {
  entry: './src/index.ts',
  target: 'node',
  mode: 'production',
  optimization: {
    usedExports: true,
    sideEffects: false,
    minimize: true
  },
  externals: {
    // Platform-specific externals
    'aws-sdk': 'aws-sdk', // Available in Lambda runtime
  }
};

// Platform-specific configurations
const platforms = {
  cloudflare: {
    ...config,
    target: 'webworker',
    externals: {} // No external dependencies
  },
  aws: {
    ...config,
    externals: {
      'aws-sdk': 'aws-sdk'
    }
  }
};
```

### 3. Compression

```json
{
  "scripts": {
    "compress": "gzip -9 dist/*.js && brotli -9 dist/*.js",
    "analyze": "webpack-bundle-analyzer dist/stats.json"
  }
}
```

## Platform-Specific Optimizations

### Cloudflare Workers

```typescript
// Optimize for CPU time limits
class CloudflareOptimizer {
  private static readonly CPU_TIME_LIMIT = 10; // ms

  static async processWithTimeLimit<T>(
    operation: () => Promise<T>
  ): Promise<T> {
    const startTime = Date.now();
    
    const result = await operation();
    
    const cpuTime = Date.now() - startTime;
    if (cpuTime > this.CPU_TIME_LIMIT * 0.8) {
      console.warn(`High CPU usage: ${cpuTime}ms`);
    }
    
    return result;
  }

  // Use KV storage for caching
  static async cacheInKV(
    kv: KVNamespace,
    key: string,
    value: string,
    ttl = 3600
  ): Promise<void> {
    await kv.put(key, value, { expirationTtl: ttl });
  }
}
```

### Netlify Functions

```typescript
// Optimize for background functions
class NetlifyOptimizer {
  static async processInBackground(
    texts: string[],
    callback: (results: any) => void
  ): Promise<void> {
    // Use Netlify's background function capability
    if (process.env.NETLIFY_BACKGROUND === 'true') {
      // Process without time constraints
      const results = await this.processLargeBatch(texts);
      callback(results);
    } else {
      // Regular function with time limits
      const results = await this.processWithTimeLimit(texts);
      callback(results);
    }
  }
}
```

### Vercel Edge Functions

```typescript
// Optimize for Edge Runtime
class VercelEdgeOptimizer {
  static optimizeForEdge(): void {
    // Use Edge-compatible APIs only
    if (typeof EdgeRuntime !== 'undefined') {
      // Running in Edge Runtime
      this.useEdgeOptimizations();
    } else {
      // Running in Node.js runtime
      this.useNodeOptimizations();
    }
  }

  private static useEdgeOptimizations(): void {
    // Smaller cache for edge environment
    process.env.UROMAN_CACHE_SIZE = '1000';
  }
}
```

## Performance Monitoring

### 1. Metrics Collection

```typescript
class PerformanceMetrics {
  private static metrics = new Map<string, number[]>();

  static recordMetric(name: string, value: number): void {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    
    const values = this.metrics.get(name)!;
    values.push(value);
    
    // Keep only last 100 measurements
    if (values.length > 100) {
      values.shift();
    }
  }

  static getStats(name: string): PerformanceStats {
    const values = this.metrics.get(name) || [];
    if (values.length === 0) {
      return { avg: 0, min: 0, max: 0, p95: 0 };
    }

    const sorted = [...values].sort((a, b) => a - b);
    return {
      avg: values.reduce((sum, v) => sum + v, 0) / values.length,
      min: sorted[0],
      max: sorted[sorted.length - 1],
      p95: sorted[Math.floor(sorted.length * 0.95)]
    };
  }
}
```

### 2. Performance Profiling

```typescript
class Profiler {
  static async profile<T>(
    name: string,
    operation: () => Promise<T>
  ): Promise<T> {
    const startTime = Date.now();
    const startMemory = process.memoryUsage();
    
    try {
      const result = await operation();
      
      const endTime = Date.now();
      const endMemory = process.memoryUsage();
      
      const duration = endTime - startTime;
      const memoryDelta = endMemory.heapUsed - startMemory.heapUsed;
      
      PerformanceMetrics.recordMetric(`${name}_duration`, duration);
      PerformanceMetrics.recordMetric(`${name}_memory`, memoryDelta);
      
      console.log(`${name}: ${duration}ms, ${Math.round(memoryDelta / 1024)}KB`);
      
      return result;
    } catch (error) {
      PerformanceMetrics.recordMetric(`${name}_errors`, 1);
      throw error;
    }
  }
}
```

## Performance Testing

### Load Testing Script

```typescript
// performance-test.ts
import { performance } from 'perf_hooks';

class LoadTester {
  async runLoadTest(
    endpoint: string,
    concurrency: number,
    duration: number
  ): Promise<LoadTestResult> {
    const results: RequestResult[] = [];
    const startTime = performance.now();
    const endTime = startTime + duration * 1000;
    
    const workers = Array(concurrency).fill(0).map(() => 
      this.runWorker(endpoint, endTime, results)
    );
    
    await Promise.all(workers);
    
    return this.analyzeResults(results);
  }

  private async runWorker(
    endpoint: string,
    endTime: number,
    results: RequestResult[]
  ): Promise<void> {
    while (performance.now() < endTime) {
      const start = performance.now();
      
      try {
        const response = await fetch(endpoint, {
          method: 'POST',
          body: JSON.stringify({
            method: 'tools/call',
            params: {
              name: 'romanize',
              arguments: { text: 'Test текст' }
            }
          })
        });
        
        const end = performance.now();
        
        results.push({
          success: response.ok,
          duration: end - start,
          status: response.status
        });
      } catch (error) {
        results.push({
          success: false,
          duration: performance.now() - start,
          error: error.message
        });
      }
      
      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 10));
    }
  }
}
```

## Troubleshooting Performance Issues

### Common Issues and Solutions

1. **High Cold Start Times**
   - Reduce bundle size
   - Minimize top-level imports
   - Use lazy loading
   - Pre-compile dependencies

2. **Memory Leaks**
   - Monitor cache sizes
   - Clear references after use
   - Use WeakMap for temporary data
   - Force garbage collection

3. **Slow Response Times**
   - Implement caching
   - Optimize algorithms
   - Use batch processing
   - Profile bottlenecks

4. **Timeout Errors**
   - Break large operations into chunks
   - Use streaming responses
   - Implement async processing
   - Optimize critical paths

### Performance Debugging

```bash
# Enable performance logging
DEBUG=performance npm run dev

# Profile memory usage
node --inspect --heap-prof src/index.js

# Analyze bundle size
npm run build && npm run analyze

# Run performance tests
npm run test:performance
```
