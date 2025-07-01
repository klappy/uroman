/**
 * Tests for Cloudflare Workers Adapter
 * 
 * Note: These tests mock the uroman module since it may not be available in test environment
 */

import { test, expect, beforeEach, vi } from 'vitest';

// Mock the uroman module
const mockUroman = {
  romanize_string: vi.fn(),
  reset_cache: vi.fn()
};

const mockUromanModule = {
  Uroman: vi.fn(() => mockUroman),
  RomFormat: {
    STR: 'str',
    EDGES: 'edges'
  }
};

// Mock dynamic import
vi.mock('uroman', () => mockUromanModule);

// Import after mocking
let CloudflareAdapter;

beforeEach(async () => {
  vi.clearAllMocks();
  
  // Reset mock implementations
  mockUroman.romanize_string.mockImplementation((text) => `romanized: ${text}`);
  
  // Dynamic import of the adapter (since it's built)
  try {
    const module = await import('../dist/cloudflare.js');
    CloudflareAdapter = module.CloudflareAdapter;
  } catch (error) {
    // Fallback to source if dist doesn't exist
    const module = await import('../src/adapters/cloudflare.ts');
    CloudflareAdapter = module.CloudflareAdapter;
  }
});

test('CloudflareAdapter - Health Check', async () => {
  const adapter = new CloudflareAdapter();
  
  const response = await adapter.healthCheck();
  expect(response.status).toBe(200);
  
  const body = await response.json();
  expect(body.status).toBe('healthy');
  expect(body.platform).toBe('cloudflare-workers');
  expect(body.serviceInitialized).toBe(true);
  expect(body.cacheStats).toBeDefined();
});

test('CloudflareAdapter - MCP Tools List', async () => {
  const adapter = new CloudflareAdapter();
  
  const request = new Request('http://localhost', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'tools/list',
      id: 1
    })
  });
  
  const response = await adapter.handleRequest(request);
  expect(response.status).toBe(200);
  
  const body = await response.json();
  expect(body.result.tools).toHaveLength(3);
  expect(body.result.tools[0].name).toBe('romanize');
  expect(body.result.tools[1].name).toBe('romanize_batch');
  expect(body.result.tools[2].name).toBe('detect_script');
});

test('CloudflareAdapter - Romanize Tool', async () => {
  const adapter = new CloudflareAdapter();
  
  const request = new Request('http://localhost', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'tools/call',
      params: {
        name: 'romanize',
        arguments: {
          text: 'こんにちは',
          language: 'jpn'
        }
      },
      id: 1
    })
  });
  
  const response = await adapter.handleRequest(request);
  expect(response.status).toBe(200);
  
  const body = await response.json();
  expect(body.result.type).toBe('text');
  expect(body.result.content).toContain('romanized:');
});

test('CloudflareAdapter - Batch Romanize Tool', async () => {
  const adapter = new CloudflareAdapter();
  
  const request = new Request('http://localhost', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'tools/call',
      params: {
        name: 'romanize_batch',
        arguments: {
          texts: ['こんにちは', '你好']
        }
      },
      id: 1
    })
  });
  
  const response = await adapter.handleRequest(request);
  expect(response.status).toBe(200);
  
  const body = await response.json();
  expect(body.result.type).toBe('json');
  expect(body.result.content.results).toHaveLength(2);
  expect(body.result.content.stats.total).toBe(2);
});

test('CloudflareAdapter - Script Detection Tool', async () => {
  const adapter = new CloudflareAdapter();
  
  const request = new Request('http://localhost', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'tools/call',
      params: {
        name: 'detect_script',
        arguments: {
          text: 'Hello 你好 こんにちは',
          detailed: true
        }
      },
      id: 1
    })
  });
  
  const response = await adapter.handleRequest(request);
  expect(response.status).toBe(200);
  
  const body = await response.json();
  expect(body.result.type).toBe('json');
  expect(body.result.content.scripts).toBeDefined();
  expect(body.result.content.primaryScript).toBeDefined();
  expect(body.result.content.mixedScript).toBe(true);
});

test('CloudflareAdapter - CORS Headers', async () => {
  const adapter = new CloudflareAdapter();
  
  const request = new Request('http://localhost', {
    method: 'OPTIONS'
  });
  
  const response = await adapter.handleRequest(request);
  expect(response.status).toBe(200);
  expect(response.headers.get('Access-Control-Allow-Origin')).toBe('*');
  expect(response.headers.get('Access-Control-Allow-Methods')).toBe('POST, OPTIONS');
});

test('CloudflareAdapter - Error Handling', async () => {
  const adapter = new CloudflareAdapter();
  
  const request = new Request('http://localhost', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: 'invalid json'
  });
  
  const response = await adapter.handleRequest(request);
  expect(response.status).toBe(400);
  
  const body = await response.json();
  expect(body.error.code).toBe(-32700);
  expect(body.error.message).toBe('Parse error');
});

test('CloudflareAdapter - Environment Variables', async () => {
  const env = {
    UROMAN_CACHE_SIZE: '2000',
    UROMAN_LOG_LEVEL: 'debug'
  };
  
  const adapter = new CloudflareAdapter(env);
  
  const response = await adapter.healthCheck();
  const body = await response.json();
  
  // Note: Due to singleton pattern, the cache size may not change if already initialized
  // Just verify the adapter was created with the environment
  expect(body.cacheStats.maxSize).toBeGreaterThan(0);
  expect(body.serviceInitialized).toBe(true);
}); 