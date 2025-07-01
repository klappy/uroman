#!/usr/bin/env node

/**
 * Build script for Cloudflare Workers deployment
 * Bundles the TypeScript code into a single JavaScript file
 */

const esbuild = require('esbuild');
const path = require('path');
const fs = require('fs');

async function buildCloudflareWorker() {
  const startTime = Date.now();
  
  console.log('🔨 Building uroman MCP server for Cloudflare Workers...');

  try {
    // Ensure dist directory exists at root level for Cloudflare Pages
    const distDir = path.join(__dirname, '../../../dist');
    if (!fs.existsSync(distDir)) {
      fs.mkdirSync(distDir, { recursive: true });
    }

    // Build configuration for Cloudflare Workers
    const buildOptions = {
      entryPoints: [path.join(__dirname, '../../../src/adapters/cloudflare.ts')],
      bundle: true,
      minify: true,
      sourcemap: false,
      outfile: path.join(distDir, 'cloudflare.js'),
      format: 'esm',
      target: 'es2022',
      platform: 'browser', // Workers use browser-like environment
      external: [],
      define: {
        'process.env.NODE_ENV': '"production"',
        'global': 'globalThis'
      },
      banner: {
        js: `// uroman MCP Server for Cloudflare Workers
// Built on ${new Date().toISOString()}
// Bundle optimized for Workers runtime`
      },
      loader: {
        '.txt': 'text',
        '.json': 'json'
      },
      resolveExtensions: ['.ts', '.js', '.json'],
      metafile: true
    };

    const result = await esbuild.build(buildOptions);
    
    // Write metafile for analysis
    const metafilePath = path.join(distDir, 'cloudflare-meta.json');
    fs.writeFileSync(metafilePath, JSON.stringify(result.metafile, null, 2));

    // Calculate bundle size
    const bundlePath = path.join(distDir, 'cloudflare.js');
    const bundleSize = fs.statSync(bundlePath).size;
    const bundleSizeKB = (bundleSize / 1024).toFixed(2);
    const bundleSizeMB = (bundleSize / 1024 / 1024).toFixed(2);

    const buildTime = Date.now() - startTime;

    console.log('✅ Build completed successfully!');
    console.log(`📦 Bundle size: ${bundleSizeKB}KB (${bundleSizeMB}MB)`);
    console.log(`⏱️  Build time: ${buildTime}ms`);
    console.log(`📄 Output: ${bundlePath}`);
    console.log(`📊 Metafile: ${metafilePath}`);
    
    // Check if bundle is within Workers limits
    const maxSizeMB = 10; // Workers limit
    if (bundleSize > maxSizeMB * 1024 * 1024) {
      console.warn(`⚠️  Warning: Bundle size (${bundleSizeMB}MB) exceeds Cloudflare Workers limit (${maxSizeMB}MB)`);
    }

    console.log('\n🚀 Ready for deployment with: wrangler deploy');

  } catch (error) {
    console.error('❌ Build failed:', error);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  buildCloudflareWorker();
}

module.exports = { buildCloudflareWorker }; 