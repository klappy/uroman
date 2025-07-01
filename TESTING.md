# Testing Guide

## Test Structure

The uroman MCP server tests are organized into discrete, focused test suites with **proper separation**:

```
/tests/                       # ROOT: Core library tests (no serverless dependencies)
├── core/
│   ├── core-logic.test.cjs          # Basic functionality (caching, validation, etc.)
│   └── uroman-integration.test.cjs  # uroman Python module integration
└── [other existing test files...]

/serverless/tests/            # SERVERLESS: MCP protocol and platform tests
├── unit/
│   └── mcp-server.test.cjs          # MCP protocol implementation
├── integration/
│   └── platform-adapters.test.cjs  # Multi-platform adapter tests
└── e2e/                             # End-to-end tests (future)
```

## Test Categories

### 🔧 Core Library Tests
**Location**: `/tests/core/` (project root)
**Purpose**: Test core uroman functionality without serverless dependencies
**Dependencies**: Python uroman module (optional for some tests)

- **Core Logic**: Script detection, caching, validation, error handling
- **uroman Integration**: Actual romanization with Python uroman module

### 🌐 Serverless MCP Tests  
**Location**: `/serverless/tests/` (serverless module)
**Purpose**: Test MCP protocol implementation and serverless wrappers
**Dependencies**: Mock MCP SDK, platform simulators

- **MCP Server Protocol**: Tool registration, request handling, error management
- **Platform Adapters**: Multi-platform deployment simulation

## Running Tests

### Quick Commands

```bash
# Run all tests
npm test

# Run only core library tests
npm run test:core

# Run only MCP/serverless tests  
npm run test:mcp

# Get help
node run-tests.js --help
```

### Direct Execution

```bash
# Individual test files
node ../tests/core/core-logic.test.cjs
node ../tests/core/uroman-integration.test.cjs
node tests/unit/mcp-server.test.cjs
node tests/integration/platform-adapters.test.cjs

# Test runner with options (from /serverless/ directory)
node run-tests.js                    # All tests
node run-tests.js --core            # Core only
node run-tests.js --mcp             # MCP only
```

## Test Dependencies

### Core Tests
- ✅ **No dependencies**: Script detection, caching, validation
- 🐍 **Python uroman**: `pip install uroman` (for full integration tests)

### Serverless Tests  
- ✅ **No dependencies**: All tests use mocks and simulators
- 📦 **Mock implementations**: MCP SDK, platform environments

## Test Output

Each test provides:
- ✅ **Pass/Fail status** for each component
- 📊 **Performance metrics** (timing, memory)
- 🔍 **Detailed output** for debugging
- 📋 **Summary reports** with next steps

## Development Workflow

1. **Start with core tests**: Verify basic functionality
2. **Add integration tests**: Test uroman module integration  
3. **Test MCP protocol**: Verify serverless wrapper
4. **Validate platform adapters**: Test deployment simulation

## Continuous Integration

The test structure supports CI/CD with:
- **Fast core tests** for quick feedback
- **Comprehensive integration tests** for full validation
- **Platform-specific test isolation**
- **Clear pass/fail reporting**

## Adding New Tests

### Core Library Tests
Add to `../tests/core/` for:
- New uroman features
- Additional script support
- Performance optimizations

### Serverless Tests
Add to `./tests/` for:
- New MCP tools/resources
- Platform-specific features  
- Deployment configurations

## Troubleshooting

### uroman Not Found
```bash
pip install uroman
# or
python3 -m pip install uroman
```

### Test Runner Issues
```bash
# Verify test files exist
ls -la ../tests/core/
ls -la tests/unit/
ls -la tests/integration/

# Run individual tests directly
node ../tests/core/core-logic.test.js
```

### Platform Adapter Tests
All platform tests use mocks - no actual deployment required for testing. 