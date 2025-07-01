// Core MCP types
export interface MCPRequest {
  method: string;
  params?: any;
  id?: string | number;
}

export interface MCPResponse {
  result?: any;
  error?: MCPError;
  id?: string | number;
}

export interface MCPError {
  code: string;
  message: string;
  details?: any;
}

// Romanization types
export interface RomanizeParams {
  text: string;
  language?: string;
  format?: 'str' | 'edges';
}

export interface RomanizeBatchParams {
  texts: string[];
  language?: string;
}

export interface DetectScriptParams {
  text: string;
  detailed?: boolean;
}

export interface RomanizationResult {
  index: number;
  original: string;
  romanized: string;
  success: boolean;
  error?: string;
}

export interface BatchResult {
  results: RomanizationResult[];
  stats: {
    total: number;
    successful: number;
    failed: number;
    processingTime: number;
  };
}

export interface RomanizationEdge {
  start: number;
  end: number;
  original: string;
  romanized: string;
  confidence?: number;
}

export interface ScriptInfo {
  name: string;
  code: string;
  percentage: number;
  characterCount: number;
}

export interface ScriptDetectionResult {
  scripts: ScriptInfo[];
  primaryScript: string;
  mixedScript: boolean;
  details?: Array<{
    char: string;
    script: string;
  }>;
}

// Tool definitions
export interface MCPTool {
  name: string;
  description: string;
  parameters: {
    type: 'object';
    properties: Record<string, any>;
    required?: string[];
  };
}

export interface ToolResult {
  type: 'text' | 'json';
  content: string | any;
}

// Resource types
export interface MCPResource {
  uri: string;
  name: string;
  description?: string;
  mimeType?: string;
}

export interface ResourceContent {
  type: 'text' | 'json' | 'binary';
  content: string | any;
  mimeType: string;
}

// Language and script data
export interface LanguageInfo {
  code: string;
  name: string;
  script: string;
  nativeName?: string;
}

export interface SupportedScript {
  name: string;
  code: string;
  direction: 'ltr' | 'rtl';
  languages: string[];
  characterCount: number;
}

// Error codes
export const ERROR_CODES = {
  INVALID_INPUT: 'INVALID_INPUT',
  TEXT_TOO_LONG: 'TEXT_TOO_LONG',
  INVALID_LANGUAGE_CODE: 'INVALID_LANGUAGE_CODE',
  UNSUPPORTED_SCRIPT: 'UNSUPPORTED_SCRIPT',
  ROMANIZATION_FAILED: 'ROMANIZATION_FAILED',
  TIMEOUT: 'TIMEOUT',
  RATE_LIMITED: 'RATE_LIMITED',
  INTERNAL_ERROR: 'INTERNAL_ERROR'
} as const;

export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES];

// Configuration
export interface UromanConfig {
  cacheSize?: number;
  maxTextLength?: number;
  maxBatchSize?: number;
  rateLimitRpm?: number;
  debug?: boolean;
}

// Platform adapter interface
export interface PlatformAdapter {
  handleRequest(request: any): Promise<any>;
  formatResponse(response: MCPResponse): any;
}

// Performance monitoring
export interface PerformanceMetrics {
  coldStartTime?: number;
  responseTime: number;
  memoryUsage?: number;
  cacheHitRate?: number;
}

export interface BenchmarkResult {
  averageDuration: number;
  accuracy: number;
  results: Array<{
    input: string;
    expected: string;
    actual: string;
    duration: number;
    correct: boolean;
  }>;
} 