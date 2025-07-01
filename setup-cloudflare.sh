#!/bin/bash

# uroman MCP Server - Cloudflare Workers Setup Script
# This script helps you set up automated deployment to Cloudflare Workers

set -e

echo "🚀 uroman MCP Server - Cloudflare Workers Setup"
echo "================================================"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: This directory is not a git repository."
    echo "   Please run 'git init' first."
    exit 1
fi

# Check if serverless directory exists
if [ ! -d "serverless" ]; then
    echo "❌ Error: serverless directory not found."
    echo "   Please run this script from the uroman project root."
    exit 1
fi

echo "✅ Repository structure verified"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
cd serverless
npm install
cd ..

# Test the build
echo ""
echo "🔨 Testing build process..."
cd serverless
npm run build:cloudflare
cd ..

echo "✅ Build successful!"

# Check if wrangler.toml exists
if [ -f "wrangler.toml" ]; then
    echo "✅ wrangler.toml configuration found"
else
    echo "❌ wrangler.toml not found"
    exit 1
fi

# Check if GitHub Actions workflow exists
if [ -f ".github/workflows/deploy-cloudflare.yml" ]; then
    echo "✅ GitHub Actions workflow configured"
else
    echo "❌ GitHub Actions workflow not found"
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "=============="
echo ""
echo "1. 🔐 Set up Cloudflare API Token:"
echo "   • Go to: https://dash.cloudflare.com/profile/api-tokens"
echo "   • Create token with permissions:"
echo "     - Zone:Zone:Read"
echo "     - Zone:Zone Settings:Edit"
echo "     - Account:Cloudflare Workers:Edit"
echo ""
echo "2. 🔑 Add to GitHub Secrets:"
echo "   • Go to: Settings > Secrets and variables > Actions"
echo "   • Add secret: CLOUDFLARE_API_TOKEN"
echo "   • Value: Your API token from step 1"
echo ""
echo "3. 🚀 Deploy Options:"
echo ""
echo "   Option A - GitHub Actions (Recommended):"
echo "   ----------------------------------------"
echo "   git add ."
echo "   git commit -m \"Deploy uroman MCP server to Cloudflare Workers\""
echo "   git push origin main"
echo ""
echo "   Option B - Manual with Wrangler CLI:"
echo "   ------------------------------------"
echo "   npm install -g wrangler"
echo "   wrangler login"
echo "   wrangler deploy"
echo ""
echo "   Option C - Cloudflare Dashboard:"
echo "   -------------------------------"
echo "   • Go to: https://dash.cloudflare.com"
echo "   • Workers & Pages > Create > Connect to Git"
echo "   • Select this repository"
echo "   • Build command: cd serverless && npm install && npm run build:cloudflare"
echo "   • Build output: serverless/dist"
echo ""
echo "4. 🧪 Test Deployment:"
echo "   curl https://uroman-mcp-server.your-subdomain.workers.dev/health"
echo ""
echo "📖 For detailed instructions, see: CLOUDFLARE_DEPLOYMENT.md"
echo ""
echo "💡 Tip: The worker will be available at:"
echo "   https://uroman-mcp-server.your-subdomain.workers.dev"
echo ""
echo "🎯 Happy deploying!" 