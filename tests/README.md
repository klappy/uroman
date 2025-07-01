# Core Library Tests

This directory contains tests for the core uroman functionality, independent of any serverless or MCP implementations.

## Structure

```
tests/
├── core/                           # JavaScript core functionality tests
│   ├── core-logic.test.cjs        # Basic functionality (caching, validation, etc.)
│   └── uroman-integration.test.cjs # uroman Python module integration
├── test_integration_final.py      # Python comprehensive integration tests
├── run-core-tests.cjs             # Test runner for JavaScript core tests
└── README.md                      # This file
```

## Running Tests

### Quick Start
```bash
# From the tests/ directory

# Run JavaScript core tests
node run-core-tests.cjs

# Run Python integration tests
python3 -m pytest test_integration_final.py -v
```

### Individual Tests
```bash
# JavaScript tests
node core/core-logic.test.cjs                    # Core logic (no dependencies)
node core/uroman-integration.test.cjs            # uroman integration

# Python tests (requires: pip install uroman pytest)
python3 -m pytest test_integration_final.py -v  # Comprehensive integration tests
```

## Test Categories

### JavaScript Core Tests

#### Core Logic (`core-logic.test.cjs`)
Tests fundamental functionality without external dependencies:
- ✅ Script detection using Unicode ranges
- ✅ LRU caching with proper eviction
- ✅ Input validation and sanitization
- ✅ Error handling and custom error types
- ✅ Performance monitoring

#### uroman Integration (`uroman-integration.test.cjs`)
Tests integration with the Python uroman module:
- ✅ uroman module availability detection
- ✅ Text romanization across multiple languages
- ✅ Batch processing capabilities
- ✅ Script detection functionality

### Python Integration Tests

#### Comprehensive Integration (`test_integration_final.py`)
Comprehensive tests for the Python uroman package (19 tests):
- ✅ Basic romanization across multiple scripts (Russian, Greek, Hindi, etc.)
- ✅ Mixed script handling
- ✅ Number conversion from various scripts
- ✅ Edge and lattice format outputs
- ✅ File-based romanization
- ✅ Special characters and punctuation
- ✅ Unicode escape sequence handling
- ✅ Language-specific romanization rules
- ✅ Caching performance
- ✅ Braille romanization
- ✅ JSON output format
- ✅ CLI interface testing
- ✅ Serverless readiness (import time, memory usage)

## Dependencies

### JavaScript Tests
- **Core Logic**: None - Pure JavaScript functionality
- **uroman Integration**: Python uroman module (`pip install uroman`)
  - Falls back gracefully if uroman is not available

### Python Tests
- **Python uroman module**: `pip install uroman`
- **pytest**: `pip install pytest`
- **psutil**: `pip install psutil` (for memory usage tests)

## Output

Each test provides:
- ✅ Pass/fail status for each component
- 📊 Performance metrics where applicable
- 🔍 Detailed test output for debugging
- 📋 Summary with next steps

## Usage in CI/CD

These tests are designed to be:
- **Fast** - No external service dependencies
- **Reliable** - Deterministic with known inputs/outputs
- **Independent** - Can run without serverless infrastructure
- **Comprehensive** - Cover all core functionality

## Integration

The core library tests validate functionality that can be used in:
- Serverless MCP implementations
- Standalone applications
- Other integration projects
- Direct uroman usage

## Adding New Tests

Add new core functionality tests to the `core/` directory following the existing patterns:
- Use `.cjs` extension for CommonJS compatibility
- Include comprehensive test coverage
- Provide clear pass/fail indicators
- Document any external dependencies 