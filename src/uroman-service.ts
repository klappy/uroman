import { Logger } from './utils/logger.js';
import type { 
  RomanizeParams, 
  RomanizeBatchParams, 
  DetectScriptParams,
  RomanizationResult,
  BatchResult,
  ScriptDetectionResult,
  RomanizationEdge,
  UromanConfig,
  ErrorCode
} from './types/index.js';
import { ERROR_CODES } from './types/index.js';

// Dynamic import type for uroman
interface UromanInstance {
  romanize_string(text: string, lcode?: string, rom_format?: any): string | any[];
  reset_cache(): void;
}

interface UromanModule {
  Uroman: new (config?: any) => UromanInstance;
  RomFormat: {
    STR: any;
    EDGES: any;
    ALTS: any;
    LATTICE: any;
  };
}

export class MCPError extends Error {
  constructor(
    public code: ErrorCode,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'MCPError';
  }
}

export class UromanService {
  private static instance: UromanService | null = null;
  private uromanInstance: UromanInstance | null = null;
  private uromanModule: UromanModule | null = null;
  private initPromise: Promise<UromanInstance> | null = null;
  private cache = new Map<string, string>();
  private config: UromanConfig;

  private constructor(config: UromanConfig = {}) {
    this.config = {
      cacheSize: 32768, // Default smaller cache for serverless
      maxTextLength: 10000,
      maxBatchSize: 100,
      rateLimitRpm: 100,
      debug: false,
      ...config
    };

    Logger.debug('UromanService initialized with config:', this.config);
  }

  static getInstance(config?: UromanConfig): UromanService {
    if (!this.instance) {
      this.instance = new UromanService(config);
    }
    return this.instance;
  }

  private async loadUroman(): Promise<UromanInstance> {
    const startTime = Date.now();
    Logger.info('Loading uroman module...');

    try {
      // Dynamic import to avoid loading at module level
      // Note: This will be resolved at runtime when uroman is available
      const uromanModule = await import('uroman') as any;
      this.uromanModule = uromanModule;
      
      if (!this.uromanModule) {
        throw new Error('Failed to load uroman module');
      }

      this.uromanInstance = new this.uromanModule.Uroman({
        cache_size: this.config.cacheSize,
        load_log: this.config.debug
      });

      const loadTime = Date.now() - startTime;
      Logger.info(`Uroman loaded successfully in ${loadTime}ms`);
      Logger.memory('uroman-load');

      return this.uromanInstance;
    } catch (error) {
      Logger.error('Failed to load uroman:', error as Error);
      throw new MCPError(
        ERROR_CODES.INTERNAL_ERROR,
        'Failed to initialize uroman',
        { originalError: error }
      );
    }
  }

  private async getUroman(): Promise<UromanInstance> {
    if (this.uromanInstance) {
      return this.uromanInstance;
    }

    if (this.initPromise) {
      return this.initPromise;
    }

    this.initPromise = this.loadUroman();
    this.uromanInstance = await this.initPromise;
    this.initPromise = null;

    return this.uromanInstance;
  }

  private generateCacheKey(text: string, language?: string, format?: string): string {
    return `${text}:${language || 'auto'}:${format || 'str'}`;
  }

  private validateInput(text: string): void {
    if (typeof text !== 'string') {
      throw new MCPError(
        ERROR_CODES.INVALID_INPUT,
        'Text must be a string'
      );
    }

    if (text.length > this.config.maxTextLength!) {
      throw new MCPError(
        ERROR_CODES.TEXT_TOO_LONG,
        `Text exceeds maximum length of ${this.config.maxTextLength} characters`,
        { length: text.length, maxLength: this.config.maxTextLength }
      );
    }
  }

  private validateLanguageCode(language?: string): void {
    if (language && !/^[a-z]{3}$/.test(language)) {
      throw new MCPError(
        ERROR_CODES.INVALID_LANGUAGE_CODE,
        `Invalid language code: ${language}. Must be a 3-letter ISO 639-3 code.`,
        { provided: language }
      );
    }
  }

  async romanize(params: RomanizeParams): Promise<string | RomanizationEdge[]> {
    const startTime = Date.now();
    
    try {
      this.validateInput(params.text);
      this.validateLanguageCode(params.language);

      // Check cache for string format
      if (params.format === 'str' || !params.format) {
        const cacheKey = this.generateCacheKey(params.text, params.language, 'str');
        const cached = this.cache.get(cacheKey);
        if (cached) {
          Logger.debug(`Cache hit for: ${params.text.substring(0, 50)}...`);
          return cached;
        }
      }

      const uroman = await this.getUroman();
      
      let result: string | any[];
      if (params.format === 'edges') {
        result = uroman.romanize_string(
          params.text, 
          params.language, 
          this.uromanModule!.RomFormat.EDGES
        );
      } else {
        result = uroman.romanize_string(
          params.text, 
          params.language, 
          this.uromanModule!.RomFormat.STR
        );
      }

      // Cache string results
      if (typeof result === 'string') {
        const cacheKey = this.generateCacheKey(params.text, params.language, 'str');
        this.addToCache(cacheKey, result);
      }

      const duration = Date.now() - startTime;
      Logger.performance('romanize', duration);

      return result;
    } catch (error) {
      if (error instanceof MCPError) {
        throw error;
      }
      
      Logger.error('Romanization failed:', error as Error);
      throw new MCPError(
        ERROR_CODES.ROMANIZATION_FAILED,
        'Failed to romanize text',
        { originalError: error, text: params.text.substring(0, 100) }
      );
    }
  }

  async romanizeBatch(params: RomanizeBatchParams): Promise<BatchResult> {
    const startTime = Date.now();

    try {
      if (!Array.isArray(params.texts)) {
        throw new MCPError(
          ERROR_CODES.INVALID_INPUT,
          'Texts must be an array'
        );
      }

      if (params.texts.length > this.config.maxBatchSize!) {
        throw new MCPError(
          ERROR_CODES.INVALID_INPUT,
          `Batch size exceeds maximum of ${this.config.maxBatchSize}`,
          { size: params.texts.length, maxSize: this.config.maxBatchSize }
        );
      }

      this.validateLanguageCode(params.language);

      const results: RomanizationResult[] = [];
      let successful = 0;
      let failed = 0;

      for (const [index, text] of params.texts.entries()) {
        try {
          const romanizeParams: RomanizeParams = {
            text,
            format: 'str'
          };
          
          if (params.language) {
            romanizeParams.language = params.language;
          }

          const romanized = await this.romanize(romanizeParams) as string;

          results.push({
            index,
            original: text,
            romanized,
            success: true
          });
          successful++;
        } catch (error) {
          const mcpError = error instanceof MCPError ? error : new MCPError(
            ERROR_CODES.ROMANIZATION_FAILED,
            'Failed to romanize text'
          );

          results.push({
            index,
            original: text,
            romanized: text, // Fallback to original
            success: false,
            error: mcpError.message
          });
          failed++;
        }

        // Yield control periodically for large batches
        if (index % 10 === 0 && index > 0) {
          await new Promise(resolve => setTimeout(resolve, 0));
        }
      }

      const processingTime = Date.now() - startTime;
      Logger.performance('romanize-batch', processingTime);

      return {
        results,
        stats: {
          total: params.texts.length,
          successful,
          failed,
          processingTime
        }
      };
    } catch (error) {
      if (error instanceof MCPError) {
        throw error;
      }

      Logger.error('Batch romanization failed:', error as Error);
      throw new MCPError(
        ERROR_CODES.ROMANIZATION_FAILED,
        'Failed to process batch',
        { originalError: error }
      );
    }
  }

  async detectScript(params: DetectScriptParams): Promise<ScriptDetectionResult> {
    try {
      this.validateInput(params.text);

      // Simple script detection based on Unicode ranges
      const scripts = this.analyzeScripts(params.text);
      
      if (scripts.length === 0) {
        return {
          scripts: [{ name: 'Unknown', code: 'Zyyy', percentage: 100, characterCount: params.text.length }],
          primaryScript: 'Unknown',
          mixedScript: false
        };
      }

      const primaryScript = scripts[0]?.name || 'Unknown';
      const mixedScript = scripts.length > 1;

      const result: ScriptDetectionResult = {
        scripts,
        primaryScript,
        mixedScript
      };

      if (params.detailed) {
        result.details = this.getCharacterDetails(params.text);
      }

      return result;
    } catch (error) {
      if (error instanceof MCPError) {
        throw error;
      }

      Logger.error('Script detection failed:', error as Error);
      throw new MCPError(
        ERROR_CODES.INTERNAL_ERROR,
        'Failed to detect script',
        { originalError: error }
      );
    }
  }

  private analyzeScripts(text: string) {
    const scriptCounts = new Map<string, number>();
    const scriptRanges = [
      { name: 'Latin', code: 'Latn', range: [0x0000, 0x024F] },
      { name: 'Cyrillic', code: 'Cyrl', range: [0x0400, 0x04FF] },
      { name: 'Arabic', code: 'Arab', range: [0x0600, 0x06FF] },
      { name: 'Devanagari', code: 'Deva', range: [0x0900, 0x097F] },
      { name: 'Han', code: 'Hani', range: [0x4E00, 0x9FFF] },
      { name: 'Hiragana', code: 'Hira', range: [0x3040, 0x309F] },
      { name: 'Katakana', code: 'Kana', range: [0x30A0, 0x30FF] },
      { name: 'Hangul', code: 'Hang', range: [0xAC00, 0xD7AF] },
      { name: 'Thai', code: 'Thai', range: [0x0E00, 0x0E7F] },
      { name: 'Hebrew', code: 'Hebr', range: [0x0590, 0x05FF] }
    ];

    for (const char of text) {
      const codePoint = char.codePointAt(0);
      if (!codePoint) continue;

      let found = false;
      for (const script of scriptRanges) {
        if (codePoint >= script.range[0] && codePoint <= script.range[1]) {
          scriptCounts.set(script.name, (scriptCounts.get(script.name) || 0) + 1);
          found = true;
          break;
        }
      }

      if (!found && /\p{L}/u.test(char)) {
        scriptCounts.set('Other', (scriptCounts.get('Other') || 0) + 1);
      }
    }

    const totalChars = Array.from(scriptCounts.values()).reduce((sum, count) => sum + count, 0);
    
    return Array.from(scriptCounts.entries())
      .map(([name, count]) => ({
        name,
        code: scriptRanges.find(s => s.name === name)?.code || 'Zyyy',
        percentage: Math.round((count / totalChars) * 100),
        characterCount: count
      }))
      .sort((a, b) => b.characterCount - a.characterCount);
  }

  private getCharacterDetails(text: string) {
    // This is a simplified implementation
    return text.split('').slice(0, 100).map(char => ({
      char,
      script: this.getCharScript(char)
    }));
  }

  private getCharScript(char: string): string {
    const codePoint = char.codePointAt(0);
    if (!codePoint) return 'Unknown';

    if (codePoint >= 0x0000 && codePoint <= 0x024F) return 'Latin';
    if (codePoint >= 0x0400 && codePoint <= 0x04FF) return 'Cyrillic';
    if (codePoint >= 0x0600 && codePoint <= 0x06FF) return 'Arabic';
    if (codePoint >= 0x0900 && codePoint <= 0x097F) return 'Devanagari';
    if (codePoint >= 0x4E00 && codePoint <= 0x9FFF) return 'Han';
    if (codePoint >= 0x3040 && codePoint <= 0x309F) return 'Hiragana';
    if (codePoint >= 0x30A0 && codePoint <= 0x30FF) return 'Katakana';
    if (codePoint >= 0xAC00 && codePoint <= 0xD7AF) return 'Hangul';
    if (codePoint >= 0x0E00 && codePoint <= 0x0E7F) return 'Thai';
    if (codePoint >= 0x0590 && codePoint <= 0x05FF) return 'Hebrew';

    return 'Other';
  }

  private addToCache(key: string, value: string): void {
    if (this.cache.size >= this.config.cacheSize!) {
      // Simple LRU: remove oldest entry
      const firstKey = this.cache.keys().next().value;
      if (firstKey) {
        this.cache.delete(firstKey);
      }
    }
    this.cache.set(key, value);
  }

  resetCache(): void {
    this.cache.clear();
    if (this.uromanInstance) {
      this.uromanInstance.reset_cache();
    }
    Logger.info('Cache reset');
  }

  getCacheStats() {
    return {
      size: this.cache.size,
      maxSize: this.config.cacheSize,
      hitRate: 0 // TODO: Implement hit rate tracking
    };
  }
} 