# Contributing to Uroman MCP Server

## Overview

This is an external contribution to the uroman open source project, implementing a Model Context Protocol (MCP) server for serverless deployment. We welcome contributions from the community!

## Getting Started

### Prerequisites

- Node.js 18+ 
- Git
- Python 3.10+ (for uroman dependency)
- Basic understanding of MCP protocol

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/uroman.git
   cd uroman/serverless
   ```

2. **Install Dependencies**
   ```bash
   npm install
   pip install -r ../requirements.txt
   ```

3. **Run Tests**
   ```bash
   npm test
   ```

4. **Start Local Development**
   ```bash
   npm run dev
   ```

## Project Structure

```
serverless/
├── src/
│   ├── mcp-server.ts        # Core MCP server
│   ├── uroman-service.ts    # Uroman wrapper
│   └── adapters/            # Platform adapters
├── tests/                   # Test suites
├── deploy/                  # Deployment configs
└── docs/                    # Documentation
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow our coding standards:
- Use TypeScript with strict mode
- Write tests for new functionality
- Update documentation
- Follow existing code patterns

### 3. Run Quality Checks

```bash
# Run all tests
npm test

# Check code formatting
npm run lint

# Check types
npm run type-check

# Run integration tests
npm run test:integration
```

### 4. Commit Changes

Use conventional commit format:

```bash
git commit -m "feat: add batch romanization support"
git commit -m "fix: handle empty input gracefully"
git commit -m "docs: update API reference"
```

### 5. Submit Pull Request

- Push to your fork
- Create PR against main repository
- Fill out PR template
- Wait for review

## Coding Standards

### TypeScript Guidelines

```typescript
// Use explicit types
interface RomanizeParams {
  text: string;
  language?: string;
  format?: 'str' | 'edges';
}

// Use async/await over promises
async function romanizeText(params: RomanizeParams): Promise<string> {
  const result = await uromanService.romanize(params.text, params.language);
  return result;
}

// Handle errors gracefully
try {
  const result = await operation();
  return result;
} catch (error) {
  logger.error('Operation failed', { error: error.message });
  throw new MCPError('ROMANIZATION_FAILED', 'Failed to romanize text');
}
```

### Error Handling

```typescript
// Define custom error types
class MCPError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'MCPError';
  }
}

// Use consistent error codes
const ERROR_CODES = {
  INVALID_INPUT: 'INVALID_INPUT',
  TEXT_TOO_LONG: 'TEXT_TOO_LONG',
  UNSUPPORTED_LANGUAGE: 'UNSUPPORTED_LANGUAGE',
  ROMANIZATION_FAILED: 'ROMANIZATION_FAILED'
} as const;
```

### Testing Guidelines

```typescript
// Write descriptive test names
describe('UromanService', () => {
  test('should romanize Cyrillic text to Latin script', async () => {
    // Test implementation
  });

  test('should handle empty input without errors', async () => {
    // Test implementation
  });

  test('should cache results for identical inputs', async () => {
    // Test implementation
  });
});

// Use proper test structure (Arrange, Act, Assert)
test('should validate input length', async () => {
  // Arrange
  const service = new UromanService();
  const longText = 'a'.repeat(10001);

  // Act & Assert
  await expect(service.romanize(longText))
    .rejects
    .toThrow('TEXT_TOO_LONG');
});
```

## Types of Contributions

### 1. Bug Fixes

- Fix existing functionality
- Add regression tests
- Update documentation if needed

### 2. New Features

- Implement new MCP tools
- Add platform adapters
- Enhance performance

### 3. Documentation

- Improve existing docs
- Add examples
- Create tutorials

### 4. Performance Improvements

- Optimize cold start times
- Reduce memory usage
- Improve response times

## Platform Adapter Development

### Adding a New Platform

1. **Create Adapter File**
   ```typescript
   // src/adapters/new-platform.ts
   import { MCPServer } from '../mcp-server';

   export async function handler(event: any, context: any) {
     const server = new MCPServer();
     const result = await server.handleRequest(event);
     return formatResponse(result);
   }
   ```

2. **Add Build Configuration**
   ```json
   // package.json
   {
     "scripts": {
       "build:new-platform": "esbuild src/adapters/new-platform.ts --bundle --outfile=dist/new-platform.js"
     }
   }
   ```

3. **Create Deployment Guide**
   ```markdown
   # New Platform Deployment
   
   ## Prerequisites
   - Platform account
   - CLI tool installed
   
   ## Steps
   1. Configure platform.config
   2. Run build command
   3. Deploy
   ```

4. **Add Tests**
   ```typescript
   describe('New Platform Adapter', () => {
     test('should handle platform-specific request format', () => {
       // Test implementation
     });
   });
   ```

## MCP Tool Development

### Adding New Tools

1. **Define Tool Schema**
   ```typescript
   const newToolSchema = {
     name: 'new_tool',
     description: 'Description of what the tool does',
     parameters: {
       type: 'object',
       properties: {
         input: {
           type: 'string',
           description: 'Input parameter'
         }
       },
       required: ['input']
     }
   };
   ```

2. **Implement Tool Handler**
   ```typescript
   async handleNewTool(params: NewToolParams): Promise<ToolResult> {
     // Validate input
     this.validateInput(params);
     
     // Process request
     const result = await this.processNewTool(params);
     
     // Return formatted result
     return {
       type: 'text',
       content: result
     };
   }
   ```

3. **Add Tests**
   ```typescript
   describe('New Tool', () => {
     test('should process valid input correctly', async () => {
       const result = await server.handleNewTool({ input: 'test' });
       expect(result.type).toBe('text');
       expect(result.content).toBeDefined();
     });
   });
   ```

## Performance Guidelines

### Memory Optimization

```typescript
// Use lazy loading
class UromanService {
  private _instance?: Uroman;
  
  get instance(): Promise<Uroman> {
    if (!this._instance) {
      this._instance = this.loadUroman();
    }
    return this._instance;
  }
}

// Implement caching with size limits
class LRUCache<T> {
  private maxSize: number;
  private cache = new Map<string, T>();
  
  set(key: string, value: T): void {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }
}
```

### Bundle Size Optimization

```typescript
// Use dynamic imports for large dependencies
async function loadUroman(): Promise<Uroman> {
  const { Uroman } = await import('uroman');
  return new Uroman();
}

// Tree-shake unused code
export { UromanService } from './uroman-service';
// Don't export everything
```

## Documentation Standards

### API Documentation

```typescript
/**
 * Romanizes text from any script to Latin alphabet
 * 
 * @param text - Text to romanize (max 10,000 characters)
 * @param language - Optional ISO 639-3 language code
 * @param format - Output format ('str' or 'edges')
 * @returns Romanized text or edge information
 * 
 * @example
 * ```typescript
 * const result = await romanize('Привет', 'rus');
 * console.log(result); // 'Privet'
 * ```
 */
async romanize(
  text: string,
  language?: string,
  format: 'str' | 'edges' = 'str'
): Promise<string | RomanizationEdge[]>
```

### README Updates

When adding features, update relevant READMEs:
- Main serverless README
- Platform-specific guides
- API reference
- Examples

## Review Process

### Pull Request Requirements

- [ ] All tests pass
- [ ] Code coverage maintained (>90%)
- [ ] Documentation updated
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact assessed
- [ ] Security considerations addressed

### Review Checklist

**Functionality**
- [ ] Code works as intended
- [ ] Edge cases handled
- [ ] Error handling implemented

**Quality**
- [ ] Code follows style guidelines
- [ ] Tests are comprehensive
- [ ] Documentation is clear

**Performance**
- [ ] No memory leaks
- [ ] Efficient algorithms used
- [ ] Bundle size impact minimal

**Security**
- [ ] Input validation implemented
- [ ] No sensitive data exposed
- [ ] Dependencies are secure

## Release Process

### Version Numbering

We follow semantic versioning:
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features
- Patch: Bug fixes

### Release Steps

1. **Update Version**
   ```bash
   npm version patch|minor|major
   ```

2. **Update Changelog**
   ```markdown
   ## [1.1.0] - 2024-01-15
   
   ### Added
   - New batch romanization tool
   - Cloudflare Workers adapter
   
   ### Fixed
   - Memory leak in caching
   - Error handling for invalid input
   ```

3. **Create Release**
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```

4. **Deploy to Platforms**
   ```bash
   npm run deploy:all
   ```

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn
- Maintain professional communication

### Getting Help

- Check existing documentation first
- Search existing issues
- Ask questions in discussions
- Join community chat

### Reporting Issues

Use issue templates:
- Bug reports: Include reproduction steps
- Feature requests: Explain use case
- Questions: Provide context

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to the uroman MCP server!
