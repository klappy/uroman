/**
 * Cloudflare Workers Adapter for uroman MCP Server
 * 
 * Handles Workers-specific constraints:
 * - 128MB memory limit
 * - 10s execution time (free tier)
 * - 10ms CPU time per invocation
 * - Edge runtime environment
 */

import { UromanService } from '../uroman-service';
import { Logger, LogLevel } from '../utils/logger';
import type { 
  MCPRequest, 
  MCPResponse, 
  PlatformAdapter,
  RomanizeParams,
  RomanizeBatchParams,
  DetectScriptParams
} from '../types';

// Cloudflare Workers global types
declare global {
  interface KVNamespace {
    get(key: string): Promise<string | null>;
    put(key: string, value: string, options?: any): Promise<void>;
  }
  
  interface ExecutionContext {
    waitUntil(promise: Promise<any>): void;
    passThroughOnException(): void;
  }
}

interface CloudflareEnv {
  // Environment variables
  UROMAN_CACHE_SIZE?: string;
  UROMAN_LOG_LEVEL?: string;
  
  // Optional KV storage for caching
  UROMAN_CACHE?: KVNamespace;
}

export class CloudflareAdapter implements PlatformAdapter {
  private uromanService: UromanService | null = null;

  constructor(private env: CloudflareEnv = {}) {
    // Set logger context for Cloudflare
    Logger.setContext('Cloudflare-Workers');
    
    // Set log level based on environment
    const logLevel = env.UROMAN_LOG_LEVEL?.toLowerCase();
    if (logLevel === 'debug') Logger.setLevel(LogLevel.DEBUG);
    else if (logLevel === 'warn') Logger.setLevel(LogLevel.WARN);
    else if (logLevel === 'error') Logger.setLevel(LogLevel.ERROR);
    else Logger.setLevel(LogLevel.INFO);
  }

  /**
   * Initialize the uroman service with lazy loading
   * Only creates service instance when first needed
   */
  private getUromanService(): UromanService {
    if (!this.uromanService) {
      const startTime = performance.now();
      
      this.uromanService = UromanService.getInstance({
        cacheSize: parseInt(this.env.UROMAN_CACHE_SIZE || '1000'),
        maxTextLength: 10000,
        maxBatchSize: 100
      });
      
      const initTime = performance.now() - startTime;
      Logger.info('Uroman service initialized', { 
        initTime: `${initTime.toFixed(2)}ms`,
        memoryUsage: this.getMemoryUsage()
      });
    }
    
    return this.uromanService;
  }

  /**
   * Handle incoming HTTP request from Cloudflare Workers
   */
  async handleRequest(request: Request): Promise<Response> {
    const startTime = performance.now();
    
    try {
      // CORS headers for browser requests
      const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      };

      // Handle preflight requests
      if (request.method === 'OPTIONS') {
        return new Response(null, { headers: corsHeaders });
      }

      // Only accept POST requests
      if (request.method !== 'POST') {
        return new Response(JSON.stringify({
          error: 'Method not allowed. Use POST for MCP requests.'
        }), {
          status: 405,
          headers: { 
            'Content-Type': 'application/json',
            ...corsHeaders
          }
        });
      }

      // Parse request body
      let mcpRequest: MCPRequest;
      try {
        mcpRequest = await request.json() as MCPRequest;
      } catch (error) {
        return new Response(JSON.stringify({
          jsonrpc: '2.0',
          id: null,
          error: {
            code: -32700,
            message: 'Parse error',
            data: 'Invalid JSON in request body'
          }
        }), {
          status: 400,
          headers: { 
            'Content-Type': 'application/json',
            ...corsHeaders
          }
        });
      }

      // Get uroman service instance (lazy loaded)
      const uromanService = this.getUromanService();
      
      // Process MCP request
      const mcpResponse = await this.handleMCPRequest(mcpRequest, uromanService);
      
      // Log performance metrics
      const processingTime = performance.now() - startTime;
      Logger.info('Request processed', {
        method: mcpRequest.method,
        processingTime: `${processingTime.toFixed(2)}ms`,
        memoryUsage: this.getMemoryUsage()
      });

      return new Response(JSON.stringify(mcpResponse), {
        status: 200,
        headers: { 
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });

    } catch (error) {
      const processingTime = performance.now() - startTime;
      
      Logger.error('Request failed', error instanceof Error ? error : new Error('Unknown error'), {
        processingTime: `${processingTime.toFixed(2)}ms`,
        memoryUsage: this.getMemoryUsage()
      });

      return new Response(JSON.stringify({
        jsonrpc: '2.0',
        id: null,
        error: {
          code: -32603,
          message: 'Internal error',
          data: error instanceof Error ? error.message : 'Unknown error occurred'
        }
      }), {
        status: 500,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
  }

  /**
   * Get current memory usage (Workers-specific)
   */
  private getMemoryUsage(): string {
    // Cloudflare Workers doesn't expose process.memoryUsage()
    // Return a placeholder for now
    return 'N/A (Workers runtime)';
  }

  /**
   * Handle MCP request and route to appropriate tool
   */
  private async handleMCPRequest(request: MCPRequest, uromanService: UromanService): Promise<MCPResponse> {
    try {
      if (request.method === 'tools/call') {
        const { name, arguments: args } = request.params;
        
        switch (name) {
          case 'romanize':
            const romanizeResult = await uromanService.romanize(args as RomanizeParams);
            return {
              id: request.id,
              result: {
                type: 'text',
                content: typeof romanizeResult === 'string' ? romanizeResult : JSON.stringify(romanizeResult)
              }
            };
            
          case 'romanize_batch':
            const batchResult = await uromanService.romanizeBatch(args as RomanizeBatchParams);
            return {
              id: request.id,
              result: {
                type: 'json',
                content: batchResult
              }
            };
            
          case 'detect_script':
            const scriptResult = await uromanService.detectScript(args as DetectScriptParams);
            return {
              id: request.id,
              result: {
                type: 'json',
                content: scriptResult
              }
            };
            
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } else if (request.method === 'tools/list') {
        return {
          id: request.id,
          result: {
            tools: [
              {
                name: 'romanize',
                description: 'Romanize text from any script to Latin alphabet',
                parameters: {
                  type: 'object',
                  properties: {
                    text: { type: 'string', description: 'Text to romanize' },
                    language: { type: 'string', description: 'Optional 3-letter language code' },
                    format: { type: 'string', enum: ['str', 'edges'], description: 'Output format' }
                  },
                  required: ['text']
                }
              },
              {
                name: 'romanize_batch',
                description: 'Romanize multiple texts in batch',
                parameters: {
                  type: 'object',
                  properties: {
                    texts: { type: 'array', items: { type: 'string' }, description: 'Array of texts to romanize' },
                    language: { type: 'string', description: 'Optional 3-letter language code' }
                  },
                  required: ['texts']
                }
              },
              {
                name: 'detect_script',
                description: 'Detect the script(s) used in text',
                parameters: {
                  type: 'object',
                  properties: {
                    text: { type: 'string', description: 'Text to analyze' },
                    detailed: { type: 'boolean', description: 'Include character-level details' }
                  },
                  required: ['text']
                }
              }
            ]
          }
        };
      } else {
        throw new Error(`Unsupported method: ${request.method}`);
      }
    } catch (error) {
      return {
        id: request.id,
        error: {
          code: '-32603',
          message: error instanceof Error ? error.message : 'Internal error'
        }
      };
    }
  }

  /**
   * Format response for platform (required by PlatformAdapter interface)
   */
  formatResponse(response: MCPResponse): Response {
    return new Response(JSON.stringify(response), {
      status: 200,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<Response> {
    try {
      const uromanService = this.getUromanService();
      
      return new Response(JSON.stringify({
        status: 'healthy',
        platform: 'cloudflare-workers',
        timestamp: new Date().toISOString(),
        serviceInitialized: !!uromanService,
        cacheStats: uromanService.getCacheStats()
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      return new Response(JSON.stringify({
        status: 'unhealthy',
        platform: 'cloudflare-workers',
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error'
      }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
}

/**
 * Main entry point for Cloudflare Workers
 * This is the default export that Workers will call
 */
export default {
  async fetch(request: Request, env: CloudflareEnv, ctx: ExecutionContext): Promise<Response> {
    const adapter = new CloudflareAdapter(env);
    
    // Handle health check endpoint
    const url = new URL(request.url);
    if (url.pathname === '/health') {
      return adapter.healthCheck();
    }
    
    // Handle MCP requests
    return adapter.handleRequest(request);
  }
};

// Export types for external use
export type { CloudflareEnv }; 