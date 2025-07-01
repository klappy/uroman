# Uroman MCP Server for Serverless Deployment

This directory contains the implementation and documentation for deploying uroman as a Model Context Protocol (MCP) server on various serverless platforms.

## Overview

The uroman MCP server provides universal romanization capabilities through the MCP protocol, allowing AI assistants and other MCP clients to convert text in any script to the Latin alphabet. This implementation is optimized for serverless deployment with minimal cold start times and cost-effective operation.

## Documentation

- [Architecture Overview](./ARCHITECTURE.md) - System design and component structure
- [Implementation Plan](./IMPLEMENTATION_PLAN.md) - Detailed development roadmap
- [Platform Comparison](./PLATFORM_COMPARISON.md) - Serverless platform analysis and recommendations
- [MCP API Reference](./MCP_API_REFERENCE.md) - Available tools and resources
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Step-by-step deployment instructions
- [Testing Strategy](./TESTING_STRATEGY.md) - Local and integration testing approaches

## Quick Start

1. **Choose a platform** - See [Platform Comparison](./PLATFORM_COMPARISON.md) for recommendations
2. **Set up local development** - Follow the [Testing Strategy](./TESTING_STRATEGY.md)
3. **Deploy** - Use the appropriate guide in [Deployment Guide](./DEPLOYMENT_GUIDE.md)

## Project Structure

```
serverless/
├── src/
│   ├── mcp-server.ts        # Core MCP server implementation
│   ├── uroman-service.ts    # Uroman wrapper service
│   └── adapters/            # Platform-specific adapters
│       ├── cloudflare.ts    
│       ├── netlify.ts       
│       ├── vercel.ts        
│       ├── aws-lambda.ts    
│       └── local.ts         # For local testing
├── deploy/
│   ├── cloudflare/
│   ├── netlify/
│   └── vercel/
├── tests/
│   ├── integration/
│   └── performance/
└── docs/                    # This documentation
```

## Key Features

- **Universal Script Support** - Romanize text from 250+ languages
- **MCP Protocol** - Standard interface for AI assistants
- **Serverless Optimized** - Fast cold starts, minimal memory usage
- **Multi-Platform** - Deploy to Cloudflare, Netlify, Vercel, or AWS
- **Cost Effective** - Designed for free tier usage

## Contributing

This is an external contribution to the uroman open source project. See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on how to contribute.

## License

This MCP server implementation follows the same license as the main uroman project (Apache 2.0).
