export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

export class Logger {
  private static level: LogLevel = LogLevel.INFO;
  private static context: string = 'MCP-Server';

  static setLevel(level: LogLevel): void {
    this.level = level;
  }

  static setContext(context: string): void {
    this.context = context;
  }

  static debug(message: string, ...args: any[]): void {
    if (this.level <= LogLevel.DEBUG) {
      console.debug(`[${this.context}] DEBUG:`, message, ...args);
    }
  }

  static info(message: string, ...args: any[]): void {
    if (this.level <= LogLevel.INFO) {
      console.info(`[${this.context}] INFO:`, message, ...args);
    }
  }

  static warn(message: string, ...args: any[]): void {
    if (this.level <= LogLevel.WARN) {
      console.warn(`[${this.context}] WARN:`, message, ...args);
    }
  }

  static error(message: string, error?: Error, ...args: any[]): void {
    if (this.level <= LogLevel.ERROR) {
      console.error(`[${this.context}] ERROR:`, message, error, ...args);
    }
  }

  static performance(operation: string, duration: number): void {
    this.debug(`Performance: ${operation} took ${duration.toFixed(2)}ms`);
  }

  static memory(operation: string): void {
    if (this.level <= LogLevel.DEBUG) {
      const usage = process.memoryUsage();
      const usageMB = {
        rss: Math.round(usage.rss / 1024 / 1024),
        heapTotal: Math.round(usage.heapTotal / 1024 / 1024),
        heapUsed: Math.round(usage.heapUsed / 1024 / 1024),
        external: Math.round(usage.external / 1024 / 1024)
      };
      this.debug(`Memory after ${operation}:`, usageMB);
    }
  }
}

// Initialize logger based on environment
if (process.env.DEBUG === 'true') {
  Logger.setLevel(LogLevel.DEBUG);
} 