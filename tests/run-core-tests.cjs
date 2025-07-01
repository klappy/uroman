#!/usr/bin/env node

/**
 * Core Library Test Runner
 * Runs only the core uroman functionality tests (no serverless dependencies)
 */

const { spawn } = require('child_process');
const path = require('path');

console.log('🧪 uroman Core Library Test Suite\n');

const coreTests = [
  { name: 'Core Logic', path: './core/core-logic.test.cjs' },
  { name: 'uroman Integration', path: './core/uroman-integration.test.cjs' }
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

async function runCoreTests() {
  console.log('📋 Core Library Tests');
  console.log('   Tests core uroman functionality (no serverless dependencies)');
  console.log('═'.repeat(60));
  
  let passedTests = 0;
  const results = [];
  
  for (const test of coreTests) {
    const success = await runTest(test.path);
    results.push({ name: test.name, success });
    if (success) passedTests++;
  }
  
  // Summary
  console.log('═'.repeat(60));
  console.log('🏁 CORE TEST RESULTS');
  console.log('═'.repeat(60));
  
  results.forEach(test => {
    console.log(`${test.success ? '✅' : '❌'} ${test.name}`);
  });
  
  console.log(`\n🎯 Overall: ${passedTests}/${coreTests.length} core tests passed`);
  
  if (passedTests === coreTests.length) {
    console.log('\n🎉 ALL CORE TESTS PASSED!');
    console.log('\n📋 Core library is ready for:');
    console.log('✅ Production use');
    console.log('✅ Integration into other projects');
    console.log('✅ Serverless wrapper development');
  } else {
    console.log(`\n⚠️  ${coreTests.length - passedTests} core test(s) failed.`);
  }
  
  return passedTests === coreTests.length;
}

// Handle command line arguments
const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log('Usage: node run-core-tests.js');
  console.log('\nRuns core uroman library tests only (no serverless dependencies)');
  console.log('\nTests:');
  coreTests.forEach(test => {
    console.log(`  - ${test.name}: ${test.path}`);
  });
  process.exit(0);
}

// Run the core tests
runCoreTests().then(success => {
  process.exit(success ? 0 : 1);
}).catch(error => {
  console.error('❌ Core test runner failed:', error);
  process.exit(1);
}); 