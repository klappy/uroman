# Usage Examples

## Overview

This document provides practical examples of using the uroman MCP server across different platforms and use cases.

## Basic Usage Examples

### 1. Simple Text Romanization

```typescript
import { MCPClient } from '@modelcontextprotocol/client';

// Connect to deployed MCP server
const client = new MCPClient('https://uroman-mcp.your-domain.com');

// Basic romanization
const result = await client.callTool('romanize', {
  text: 'Здравствуйте'
});

console.log(result.content); // "Zdravstvuite"
```

### 2. Language-Specific Romanization

```typescript
// Russian text
const russian = await client.callTool('romanize', {
  text: 'Москва',
  language: 'rus'
});
console.log(russian.content); // "Moskva"

// Hindi text
const hindi = await client.callTool('romanize', {
  text: 'नमस्ते',
  language: 'hin'
});
console.log(hindi.content); // "namaste"

// Arabic text
const arabic = await client.callTool('romanize', {
  text: 'مرحبا',
  language: 'ara'
});
console.log(arabic.content); // "mrhba"
```

### 3. Batch Processing

```typescript
// Process multiple texts at once
const batchResult = await client.callTool('romanize_batch', {
  texts: [
    'Hello World',
    'Привет мир',
    '你好世界',
    'مرحبا بالعالم',
    'नमस्ते दुनिया'
  ]
});

console.log(batchResult.content.results);
/*
[
  { index: 0, original: "Hello World", romanized: "Hello World", success: true },
  { index: 1, original: "Привет мир", romanized: "Privet mir", success: true },
  { index: 2, original: "你好世界", romanized: "nihaoshijie", success: true },
  { index: 3, original: "مرحبا بالعالم", romanized: "mrhba balalm", success: true },
  { index: 4, original: "नमस्ते दुनिया", romanized: "namaste duniya", success: true }
]
*/
```

### 4. Script Detection

```typescript
// Detect writing systems in mixed text
const scriptInfo = await client.callTool('detect_script', {
  text: 'Hello мир 世界',
  detailed: true
});

console.log(scriptInfo.content);
/*
{
  scripts: [
    { name: "Latin", code: "Latn", percentage: 50, characterCount: 6 },
    { name: "Cyrillic", code: "Cyrl", percentage: 25, characterCount: 3 },
    { name: "Han", code: "Hani", percentage: 25, characterCount: 2 }
  ],
  primaryScript: "Latin",
  mixedScript: true
}
*/
```

## Platform-Specific Examples

### Cloudflare Workers

```typescript
// client.ts
export default {
  async fetch(request: Request): Promise<Response> {
    const mcpClient = new MCPClient('https://uroman-mcp.workers.dev');
    
    const url = new URL(request.url);
    const text = url.searchParams.get('text');
    const language = url.searchParams.get('lang');
    
    if (!text) {
      return new Response('Missing text parameter', { status: 400 });
    }
    
    try {
      const result = await mcpClient.callTool('romanize', {
        text,
        language: language || undefined
      });
      
      return new Response(JSON.stringify({
        original: text,
        romanized: result.content,
        language
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};
```

### Netlify Functions

```typescript
// netlify/functions/romanize.ts
import { Handler } from '@netlify/functions';
import { MCPClient } from '@modelcontextprotocol/client';

const client = new MCPClient(process.env.MCP_SERVER_URL);

export const handler: Handler = async (event, context) => {
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: 'Method not allowed'
    };
  }
  
  try {
    const { text, language, format } = JSON.parse(event.body || '{}');
    
    if (!text) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Text is required' })
      };
    }
    
    const result = await client.callTool('romanize', {
      text,
      language,
      format: format || 'str'
    });
    
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        original: text,
        romanized: result.content,
        language,
        format
      })
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
```

### Vercel API Route

```typescript
// pages/api/romanize.ts
import type { NextApiRequest, NextApiResponse } from 'next';
import { MCPClient } from '@modelcontextprotocol/client';

const client = new MCPClient(process.env.MCP_SERVER_URL);

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  const { text, language, format } = req.body;
  
  if (!text) {
    return res.status(400).json({ error: 'Text is required' });
  }
  
  try {
    const result = await client.callTool('romanize', {
      text,
      language,
      format: format || 'str'
    });
    
    res.status(200).json({
      original: text,
      romanized: result.content,
      language,
      format
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
```

## Real-World Use Cases

### 1. Multilingual Chat Application

```typescript
class MultilingualChat {
  private mcpClient: MCPClient;
  
  constructor(mcpServerUrl: string) {
    this.mcpClient = new MCPClient(mcpServerUrl);
  }
  
  async processMessage(message: string, userLanguage?: string): Promise<ProcessedMessage> {
    // Detect script if language not provided
    let detectedLanguage = userLanguage;
    if (!detectedLanguage) {
      const scriptInfo = await this.mcpClient.callTool('detect_script', {
        text: message
      });
      
      // Map primary script to likely language
      detectedLanguage = this.scriptToLanguage(scriptInfo.content.primaryScript);
    }
    
    // Romanize for searchability and logging
    const romanized = await this.mcpClient.callTool('romanize', {
      text: message,
      language: detectedLanguage
    });
    
    return {
      original: message,
      romanized: romanized.content,
      language: detectedLanguage,
      timestamp: new Date().toISOString()
    };
  }
  
  private scriptToLanguage(script: string): string {
    const scriptMap: Record<string, string> = {
      'Cyrillic': 'rus',
      'Devanagari': 'hin',
      'Arabic': 'ara',
      'Han': 'zho',
      'Hiragana': 'jpn',
      'Hangul': 'kor'
    };
    
    return scriptMap[script] || 'eng';
  }
}

// Usage
const chat = new MultilingualChat('https://uroman-mcp.example.com');

const message = await chat.processMessage('Привет! Как дела?');
console.log(message);
/*
{
  original: "Привет! Как дела?",
  romanized: "Privet! Kak dela?",
  language: "rus",
  timestamp: "2024-01-15T10:30:00.000Z"
}
*/
```

### 2. Document Processing Pipeline

```typescript
class DocumentProcessor {
  private mcpClient: MCPClient;
  
  constructor(mcpServerUrl: string) {
    this.mcpClient = new MCPClient(mcpServerUrl);
  }
  
  async processDocument(document: Document): Promise<ProcessedDocument> {
    const paragraphs = document.content.split('\n\n');
    
    // Process paragraphs in batches
    const batchSize = 50;
    const processedParagraphs: ProcessedParagraph[] = [];
    
    for (let i = 0; i < paragraphs.length; i += batchSize) {
      const batch = paragraphs.slice(i, i + batchSize);
      
      const batchResult = await this.mcpClient.callTool('romanize_batch', {
        texts: batch,
        language: document.language
      });
      
      for (const result of batchResult.content.results) {
        processedParagraphs.push({
          index: i + result.index,
          original: result.original,
          romanized: result.romanized,
          success: result.success
        });
      }
    }
    
    return {
      id: document.id,
      title: document.title,
      language: document.language,
      paragraphs: processedParagraphs,
      processedAt: new Date().toISOString()
    };
  }
}

// Usage
const processor = new DocumentProcessor('https://uroman-mcp.example.com');

const document = {
  id: 'doc-123',
  title: 'Russian Literature',
  language: 'rus',
  content: 'Война и мир\n\nТолстой написал великий роман...'
};

const processed = await processor.processDocument(document);
```

### 3. Search Engine Integration

```typescript
class SearchIndexer {
  private mcpClient: MCPClient;
  
  constructor(mcpServerUrl: string) {
    this.mcpClient = new MCPClient(mcpServerUrl);
  }
  
  async indexContent(content: SearchableContent): Promise<SearchIndex> {
    // Create searchable romanized version
    const romanized = await this.mcpClient.callTool('romanize', {
      text: content.text,
      language: content.language
    });
    
    // Detect script information for metadata
    const scriptInfo = await this.mcpClient.callTool('detect_script', {
      text: content.text,
      detailed: true
    });
    
    return {
      id: content.id,
      originalText: content.text,
      romanizedText: romanized.content,
      language: content.language,
      scripts: scriptInfo.content.scripts,
      searchTerms: this.generateSearchTerms(romanized.content),
      indexedAt: new Date().toISOString()
    };
  }
  
  private generateSearchTerms(text: string): string[] {
    return text
      .toLowerCase()
      .split(/\s+/)
      .filter(term => term.length > 2)
      .map(term => term.replace(/[^\w]/g, ''));
  }
  
  async search(query: string, language?: string): Promise<SearchResult[]> {
    // Romanize search query for consistent matching
    const romanizedQuery = await this.mcpClient.callTool('romanize', {
      text: query,
      language
    });
    
    // Perform search using romanized terms
    return this.performSearch(romanizedQuery.content);
  }
  
  private async performSearch(romanizedQuery: string): Promise<SearchResult[]> {
    // Implementation would search your index
    // This is a placeholder
    return [];
  }
}
```

## Error Handling Examples

### 1. Graceful Error Handling

```typescript
class RobustRomanizer {
  private mcpClient: MCPClient;
  private retryAttempts = 3;
  private retryDelay = 1000;
  
  constructor(mcpServerUrl: string) {
    this.mcpClient = new MCPClient(mcpServerUrl);
  }
  
  async romanizeWithRetry(
    text: string,
    language?: string
  ): Promise<RomanizationResult> {
    for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
      try {
        const result = await this.mcpClient.callTool('romanize', {
          text,
          language
        });
        
        return {
          success: true,
          original: text,
          romanized: result.content,
          attempt
        };
      } catch (error) {
        console.warn(`Attempt ${attempt} failed:`, error.message);
        
        if (attempt === this.retryAttempts) {
          return {
            success: false,
            original: text,
            romanized: text, // Fallback to original
            error: error.message,
            attempt
          };
        }
        
        // Wait before retry
        await new Promise(resolve => 
          setTimeout(resolve, this.retryDelay * attempt)
        );
      }
    }
    
    // This should never be reached, but TypeScript requires it
    throw new Error('Unexpected error in retry logic');
  }
}
```

### 2. Batch Error Handling

```typescript
class BatchRomanizer {
  private mcpClient: MCPClient;
  
  constructor(mcpServerUrl: string) {
    this.mcpClient = new MCPClient(mcpServerUrl);
  }
  
  async romanizeBatchWithFallback(
    texts: string[],
    language?: string
  ): Promise<BatchRomanizationResult> {
    try {
      // Try batch processing first
      const batchResult = await this.mcpClient.callTool('romanize_batch', {
        texts,
        language
      });
      
      return {
        method: 'batch',
        results: batchResult.content.results,
        stats: batchResult.content.stats
      };
    } catch (error) {
      console.warn('Batch processing failed, falling back to individual:', error.message);
      
      // Fallback to individual processing
      return this.romanizeIndividually(texts, language);
    }
  }
  
  private async romanizeIndividually(
    texts: string[],
    language?: string
  ): Promise<BatchRomanizationResult> {
    const results: RomanizationResult[] = [];
    let successful = 0;
    let failed = 0;
    
    for (const [index, text] of texts.entries()) {
      try {
        const result = await this.mcpClient.callTool('romanize', {
          text,
          language
        });
        
        results.push({
          index,
          original: text,
          romanized: result.content,
          success: true
        });
        successful++;
      } catch (error) {
        results.push({
          index,
          original: text,
          romanized: text, // Fallback to original
          success: false,
          error: error.message
        });
        failed++;
      }
    }
    
    return {
      method: 'individual',
      results,
      stats: {
        total: texts.length,
        successful,
        failed,
        processingTime: 0 // Not measured in this example
      }
    };
  }
}
```

## Testing Examples

### 1. Unit Testing with Mock MCP Client

```typescript
// test/romanizer.test.ts
import { describe, test, expect, vi } from 'vitest';
import { MCPClient } from '@modelcontextprotocol/client';
import { RobustRomanizer } from '../src/robust-romanizer';

// Mock the MCP client
vi.mock('@modelcontextprotocol/client');

describe('RobustRomanizer', () => {
  test('should romanize text successfully', async () => {
    const mockClient = {
      callTool: vi.fn().mockResolvedValue({
        content: 'Privet'
      })
    };
    
    (MCPClient as any).mockImplementation(() => mockClient);
    
    const romanizer = new RobustRomanizer('http://test.com');
    const result = await romanizer.romanizeWithRetry('Привет', 'rus');
    
    expect(result.success).toBe(true);
    expect(result.romanized).toBe('Privet');
    expect(mockClient.callTool).toHaveBeenCalledWith('romanize', {
      text: 'Привет',
      language: 'rus'
    });
  });
  
  test('should retry on failure', async () => {
    const mockClient = {
      callTool: vi.fn()
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValue({ content: 'Privet' })
    };
    
    (MCPClient as any).mockImplementation(() => mockClient);
    
    const romanizer = new RobustRomanizer('http://test.com');
    const result = await romanizer.romanizeWithRetry('Привет', 'rus');
    
    expect(result.success).toBe(true);
    expect(result.attempt).toBe(2);
    expect(mockClient.callTool).toHaveBeenCalledTimes(2);
  });
});
```

### 2. Integration Testing

```typescript
// test/integration.test.ts
import { describe, test, expect } from 'vitest';
import { MCPClient } from '@modelcontextprotocol/client';

describe('MCP Server Integration', () => {
  const client = new MCPClient(process.env.TEST_MCP_URL || 'http://localhost:3000');
  
  test('should handle basic romanization', async () => {
    const result = await client.callTool('romanize', {
      text: 'Тест'
    });
    
    expect(result.content).toBe('Test');
  });
  
  test('should handle batch processing', async () => {
    const result = await client.callTool('romanize_batch', {
      texts: ['Hello', 'Привет', '你好']
    });
    
    expect(result.content.results).toHaveLength(3);
    expect(result.content.stats.successful).toBe(3);
  });
  
  test('should detect scripts correctly', async () => {
    const result = await client.callTool('detect_script', {
      text: 'Hello мир'
    });
    
    expect(result.content.scripts).toHaveLength(2);
    expect(result.content.mixedScript).toBe(true);
  });
});
```

## Performance Examples

### 1. Benchmarking

```typescript
// benchmark/performance.ts
import { performance } from 'perf_hooks';
import { MCPClient } from '@modelcontextprotocol/client';

class PerformanceBenchmark {
  private client: MCPClient;
  
  constructor(serverUrl: string) {
    this.client = new MCPClient(serverUrl);
  }
  
  async benchmarkRomanization(): Promise<BenchmarkResult> {
    const testCases = [
      { text: 'Hello', expected: 'Hello' },
      { text: 'Привет', expected: 'Privet' },
      { text: 'नमस्ते', expected: 'namaste' },
      { text: 'مرحبا', expected: 'mrhba' }
    ];
    
    const results: TestResult[] = [];
    
    for (const testCase of testCases) {
      const start = performance.now();
      
      const result = await this.client.callTool('romanize', {
        text: testCase.text
      });
      
      const end = performance.now();
      const duration = end - start;
      
      results.push({
        input: testCase.text,
        expected: testCase.expected,
        actual: result.content,
        duration,
        correct: result.content === testCase.expected
      });
    }
    
    return {
      results,
      averageDuration: results.reduce((sum, r) => sum + r.duration, 0) / results.length,
      accuracy: results.filter(r => r.correct).length / results.length
    };
  }
}

// Usage
const benchmark = new PerformanceBenchmark('https://uroman-mcp.example.com');
const results = await benchmark.benchmarkRomanization();

console.log(`Average duration: ${results.averageDuration.toFixed(2)}ms`);
console.log(`Accuracy: ${(results.accuracy * 100).toFixed(1)}%`);
```

These examples demonstrate the versatility and practical applications of the uroman MCP server across different platforms and use cases. They provide a solid foundation for building your own applications that leverage universal romanization capabilities.
