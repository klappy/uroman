#!/usr/bin/env node

/**
 * Test Runner for uroman MCP Server
 * Runs tests in the proper order: Core → Integration → Serverless
 */

const { spawn } = require('child_process');
const path = require('path');

console.log('🧪 uroman MCP Server Test Suite\n');

const testSuites = [
  {
    name: 'Core Library Tests',
    description: 'Tests core uroman functionality (no dependencies)',
    tests: [
      { name: 'Core Logic', path: '../tests/core/core-logic.test.cjs' },
      { name: 'uroman Integration', path: '../tests/core/uroman-integration.test.cjs' }
    ]
  },
  {
    name: 'Serverless MCP Tests', 
    description: 'Tests MCP protocol and serverless wrapper',
    tests: [
      { name: 'MCP Server Protocol', path: './tests/unit/mcp-server.test.cjs' },
      { name: 'Platform Adapters', path: './tests/integration/platform-adapters.test.cjs' }
    ]
  }
];

function runTest(testPath) {
  return new Promise((resolve) => {
    console.log(`\n🔍 Running: ${path.basename(testPath)}`);
    console.log('─'.repeat(50));
    
    const child = spawn('node', [testPath], {
      stdio: 'inherit',
      cwd: __dirname
    });
    
    child.on('close', (code) => {
      const success = code === 0;
      console.log('─'.repeat(50));
      console.log(`${success ? '✅' : '❌'} ${path.basename(testPath)}: ${success ? 'PASSED' : 'FAILED'}\n`);
      resolve(success);
    });
    
    child.on('error', (error) => {
      console.log('─'.repeat(50));
      console.log(`❌ ${path.basename(testPath)}: ERROR - ${error.message}\n`);
      resolve(false);
    });
  });
}

async function runTestSuite() {
  let totalTests = 0;
  let passedTests = 0;
  const results = [];
  
  for (const suite of testSuites) {
    console.log(`\n📋 ${suite.name}`);
    console.log(`   ${suite.description}`);
    console.log('═'.repeat(60));
    
    const suiteResults = {
      name: suite.name,
      tests: [],
      passed: 0,
      total: suite.tests.length
    };
    
    for (const test of suite.tests) {
      totalTests++;
      const success = await runTest(test.path);
      
      suiteResults.tests.push({
        name: test.name,
        success
      });
      
      if (success) {
        passedTests++;
        suiteResults.passed++;
      }
    }
    
    results.push(suiteResults);
    
    console.log(`📊 Suite Summary: ${suiteResults.passed}/${suiteResults.total} tests passed`);
  }
  
  // Final summary
  console.log('\n' + '═'.repeat(60));
  console.log('🏁 FINAL TEST RESULTS');
  console.log('═'.repeat(60));
  
  results.forEach(suite => {
    console.log(`\n📋 ${suite.name}: ${suite.passed}/${suite.total}`);
    suite.tests.forEach(test => {
      console.log(`   ${test.success ? '✅' : '❌'} ${test.name}`);
    });
  });
  
  console.log(`\n🎯 Overall: ${passedTests}/${totalTests} tests passed`);
  
  if (passedTests === totalTests) {
    console.log('\n🎉 ALL TESTS PASSED! Ready for deployment!');
    console.log('\n📋 Next Steps:');
    console.log('1. Implement platform adapters (Phase 2)');
    console.log('2. Deploy to Cloudflare Workers');
    console.log('3. Add end-to-end tests');
    console.log('4. Set up CI/CD pipeline');
  } else {
    console.log(`\n⚠️  ${totalTests - passedTests} test(s) failed. Please fix before proceeding.`);
  }
  
  return passedTests === totalTests;
}

// Handle command line arguments
const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log('Usage: node run-tests.js [options]');
  console.log('\nOptions:');
  console.log('  --core     Run only core library tests');
  console.log('  --mcp      Run only MCP/serverless tests');
  console.log('  --help     Show this help message');
  console.log('\nExamples:');
  console.log('  node run-tests.js           # Run all tests');
  console.log('  node run-tests.js --core    # Run only core tests');
  console.log('  node run-tests.js --mcp     # Run only MCP tests');
  process.exit(0);
}

// Filter test suites based on arguments
if (args.includes('--core')) {
  testSuites.splice(1); // Keep only core tests
} else if (args.includes('--mcp')) {
  testSuites.splice(0, 1); // Keep only MCP tests
}

// Run the test suite
runTestSuite().then(success => {
  process.exit(success ? 0 : 1);
}).catch(error => {
  console.error('❌ Test runner failed:', error);
  process.exit(1);
}); 