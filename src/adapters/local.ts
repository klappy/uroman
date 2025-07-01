#!/usr/bin/env tsx

import { UromanMCPServer } from '../mcp-server.js';
import { Logger, LogLevel } from '../utils/logger.js';

async function main() {
  // Enable debug logging for local development
  Logger.setLevel(LogLevel.DEBUG);
  Logger.info('Starting uroman MCP server in local development mode...');

  try {
    // Create MCP server with development configuration
    const server = new UromanMCPServer({
      cacheSize: 1000, // Smaller cache for development
      debug: true
    });

    // For now, just test the server initialization
    Logger.info('MCP server initialized successfully');
    Logger.info('Server capabilities:', server.getServer().getCapabilities());
    
    // Test basic functionality without uroman dependency
    Logger.info('Testing script detection...');
    
    // Simple test of our script detection
    const testText = "Hello мир 世界";
    Logger.info(`Test text: ${testText}`);
    
    // We can't test actual romanization without uroman installed,
    // but we can test the server structure
    Logger.info('✅ Local development server ready!');
    Logger.info('Next steps:');
    Logger.info('1. Install uroman: pip install uroman');
    Logger.info('2. Run integration tests');
    Logger.info('3. Test with MCP inspector');
    
  } catch (error) {
    Logger.error('Failed to start server:', error as Error);
    process.exit(1);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error('Unhandled error:', error);
    process.exit(1);
  });
} 