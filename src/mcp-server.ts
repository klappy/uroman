import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ErrorCode,
  McpError
} from '@modelcontextprotocol/sdk/types.js';

import { UromanService, MCPError } from './uroman-service.js';
import { Logger } from './utils/logger.js';
import type { 
  MCPTool, 
  ToolResult, 
  MCPResource, 
  ResourceContent,
  UromanConfig,
  RomanizeParams,
  RomanizeBatchParams,
  DetectScriptParams
} from './types/index.js';

export class UromanMCPServer {
  private server: Server;
  private uromanService: UromanService;

  constructor(config?: UromanConfig) {
    this.server = new Server(
      {
        name: 'uroman-mcp-server',
        version: '1.0.0',
        description: 'Universal romanization MCP server'
      },
      {
        capabilities: {
          tools: {},
          resources: {}
        }
      }
    );

    this.uromanService = UromanService.getInstance(config);
    this.setupHandlers();
    Logger.info('UromanMCPServer initialized');
  }

  private setupHandlers(): void {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: this.getTools()
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      try {
        Logger.debug(`Tool call: ${name}`, args);
        
        switch (name) {
          case 'romanize':
            return await this.handleRomanize(args as RomanizeParams);
          case 'romanize_batch':
            return await this.handleRomanizeBatch(args as RomanizeBatchParams);
          case 'detect_script':
            return await this.handleDetectScript(args as DetectScriptParams);
          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        Logger.error(`Tool call failed: ${name}`, error as Error);
        
        if (error instanceof MCPError) {
          throw new McpError(
            ErrorCode.InternalError,
            error.message,
            error.details
          );
        }
        
        throw new McpError(
          ErrorCode.InternalError,
          'Tool execution failed',
          { originalError: (error as Error).message }
        );
      }
    });

    // List available resources
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      return {
        resources: this.getResources()
      };
    });

    // Read resource content
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;
      
      try {
        return await this.handleReadResource(uri);
      } catch (error) {
        Logger.error(`Resource read failed: ${uri}`, error as Error);
        throw new McpError(
          ErrorCode.InternalError,
          `Failed to read resource: ${uri}`,
          { originalError: (error as Error).message }
        );
      }
    });
  }

  private getTools(): MCPTool[] {
    return [
      {
        name: 'romanize',
        description: 'Convert text in any script to Latin alphabet',
        parameters: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'Text to romanize (max 10,000 characters)',
              maxLength: 10000
            },
            language: {
              type: 'string',
              description: 'Optional ISO 639-3 language code (e.g., "rus" for Russian)',
              pattern: '^[a-z]{3}$'
            },
            format: {
              type: 'string',
              description: 'Output format',
              enum: ['str', 'edges'],
              default: 'str'
            }
          },
          required: ['text']
        }
      },
      {
        name: 'romanize_batch',
        description: 'Efficiently romanize multiple texts',
        parameters: {
          type: 'object',
          properties: {
            texts: {
              type: 'array',
              description: 'Array of texts to romanize',
              items: {
                type: 'string',
                maxLength: 1000
              },
              maxItems: 100
            },
            language: {
              type: 'string',
              description: 'Optional ISO 639-3 language code for all texts',
              pattern: '^[a-z]{3}$'
            }
          },
          required: ['texts']
        }
      },
      {
        name: 'detect_script',
        description: 'Detect the writing system(s) used in text',
        parameters: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'Text to analyze (max 5,000 characters)',
              maxLength: 5000
            },
            detailed: {
              type: 'boolean',
              description: 'Include character-level script information',
              default: false
            }
          },
          required: ['text']
        }
      }
    ];
  }

  private getResources(): MCPResource[] {
    return [
      {
        uri: 'uroman://languages',
        name: 'Supported Languages',
        description: 'List of supported ISO 639-3 language codes',
        mimeType: 'application/json'
      },
      {
        uri: 'uroman://scripts',
        name: 'Supported Scripts',
        description: 'List of supported writing systems',
        mimeType: 'application/json'
      },
      {
        uri: 'uroman://examples/cyrillic',
        name: 'Cyrillic Examples',
        description: 'Example romanizations for Cyrillic script',
        mimeType: 'application/json'
      },
      {
        uri: 'uroman://examples/arabic',
        name: 'Arabic Examples',
        description: 'Example romanizations for Arabic script',
        mimeType: 'application/json'
      },
      {
        uri: 'uroman://stats',
        name: 'Server Statistics',
        description: 'Cache and performance statistics',
        mimeType: 'application/json'
      }
    ];
  }

  private async handleRomanize(params: RomanizeParams): Promise<ToolResult> {
    const result = await this.uromanService.romanize(params);
    
    if (params.format === 'edges') {
      return {
        type: 'json',
        content: result
      };
    }
    
    return {
      type: 'text',
      content: result as string
    };
  }

  private async handleRomanizeBatch(params: RomanizeBatchParams): Promise<ToolResult> {
    const result = await this.uromanService.romanizeBatch(params);
    
    return {
      type: 'json',
      content: result
    };
  }

  private async handleDetectScript(params: DetectScriptParams): Promise<ToolResult> {
    const result = await this.uromanService.detectScript(params);
    
    return {
      type: 'json',
      content: result
    };
  }

  private async handleReadResource(uri: string): Promise<ResourceContent> {
    switch (uri) {
      case 'uroman://languages':
        return {
          type: 'json',
          content: this.getLanguageList(),
          mimeType: 'application/json'
        };
        
      case 'uroman://scripts':
        return {
          type: 'json',
          content: this.getScriptList(),
          mimeType: 'application/json'
        };
        
      case 'uroman://examples/cyrillic':
        return {
          type: 'json',
          content: this.getCyrillicExamples(),
          mimeType: 'application/json'
        };
        
      case 'uroman://examples/arabic':
        return {
          type: 'json',
          content: this.getArabicExamples(),
          mimeType: 'application/json'
        };
        
      case 'uroman://stats':
        return {
          type: 'json',
          content: this.uromanService.getCacheStats(),
          mimeType: 'application/json'
        };
        
      default:
        throw new Error(`Unknown resource: ${uri}`);
    }
  }

  private getLanguageList() {
    return [
      { code: 'ara', name: 'Arabic', script: 'Arabic', nativeName: 'العربية' },
      { code: 'rus', name: 'Russian', script: 'Cyrillic', nativeName: 'Русский' },
      { code: 'hin', name: 'Hindi', script: 'Devanagari', nativeName: 'हिन्दी' },
      { code: 'zho', name: 'Chinese', script: 'Han', nativeName: '中文' },
      { code: 'jpn', name: 'Japanese', script: 'Hiragana/Katakana/Han', nativeName: '日本語' },
      { code: 'kor', name: 'Korean', script: 'Hangul', nativeName: '한국어' },
      { code: 'tha', name: 'Thai', script: 'Thai', nativeName: 'ไทย' },
      { code: 'heb', name: 'Hebrew', script: 'Hebrew', nativeName: 'עברית' },
      { code: 'ell', name: 'Greek', script: 'Greek', nativeName: 'Ελληνικά' },
      { code: 'fas', name: 'Persian', script: 'Arabic', nativeName: 'فارسی' },
      { code: 'urd', name: 'Urdu', script: 'Arabic', nativeName: 'اردو' },
      { code: 'ukr', name: 'Ukrainian', script: 'Cyrillic', nativeName: 'Українська' }
    ];
  }

  private getScriptList() {
    return [
      { name: 'Latin', code: 'Latn', direction: 'ltr', languages: ['eng', 'fra', 'deu', 'spa'], characterCount: 256 },
      { name: 'Cyrillic', code: 'Cyrl', direction: 'ltr', languages: ['rus', 'ukr', 'bul'], characterCount: 256 },
      { name: 'Arabic', code: 'Arab', direction: 'rtl', languages: ['ara', 'fas', 'urd'], characterCount: 256 },
      { name: 'Devanagari', code: 'Deva', direction: 'ltr', languages: ['hin', 'mar', 'nep'], characterCount: 128 },
      { name: 'Han', code: 'Hani', direction: 'ltr', languages: ['zho', 'jpn'], characterCount: 40000 },
      { name: 'Hiragana', code: 'Hira', direction: 'ltr', languages: ['jpn'], characterCount: 96 },
      { name: 'Katakana', code: 'Kana', direction: 'ltr', languages: ['jpn'], characterCount: 96 },
      { name: 'Hangul', code: 'Hang', direction: 'ltr', languages: ['kor'], characterCount: 11172 },
      { name: 'Thai', code: 'Thai', direction: 'ltr', languages: ['tha'], characterCount: 128 },
      { name: 'Hebrew', code: 'Hebr', direction: 'rtl', languages: ['heb'], characterCount: 128 }
    ];
  }

  private getCyrillicExamples() {
    return {
      script: 'Cyrillic',
      examples: [
        { original: 'Привет', romanized: 'Privet', language: 'Russian' },
        { original: 'Москва', romanized: 'Moskva', language: 'Russian' },
        { original: 'Київ', romanized: 'Kyiv', language: 'Ukrainian' },
        { original: 'Здравствуйте', romanized: 'Zdravstvuite', language: 'Russian' },
        { original: 'Спасибо', romanized: 'Spasibo', language: 'Russian' }
      ]
    };
  }

  private getArabicExamples() {
    return {
      script: 'Arabic',
      examples: [
        { original: 'مرحبا', romanized: 'mrhba', language: 'Arabic' },
        { original: 'شكرا', romanized: 'shkra', language: 'Arabic' },
        { original: 'ایران', romanized: 'iran', language: 'Persian' },
        { original: 'نیپال', romanized: 'nipal', language: 'Urdu' },
        { original: 'السلام عليكم', romanized: 'alslam lykm', language: 'Arabic' }
      ]
    };
  }

  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    Logger.info('MCP server running on stdio');
  }

  async handleRequest(request: any): Promise<any> {
    // For HTTP-based adapters
    return await this.server.request(request);
  }

  getServer(): Server {
    return this.server;
  }
} 