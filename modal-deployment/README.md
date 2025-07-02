# Uroman on Modal.ai

Deploy the Uroman universal romanizer as a serverless API on Modal.ai.

## What is this?

This deploys uroman (a tool that converts text in any script to Latin alphabet) as a cloud service using Modal.ai. Think of it as Google Translate's alphabet-only cousin, but hosted on steroids (Modal's infrastructure).

## Available Deployments

- **Simple REST API**: `uroman_modal_simple.py` - Basic HTTP endpoint
- **MCP Server**: `uroman_mcp_modal.py` - For AI assistants (Claude, etc.)
- **Production**: `uroman_modal_production.py` - Full-featured with monitoring

## Setup

1. Install Modal:
```bash
pip install modal
```

2. Set up Modal (you'll need to create an account):
```bash
modal setup
```

3. Test locally:
```bash
# For simple REST API
modal run uroman_modal_simple.py

# For MCP server
modal run uroman_mcp_modal.py
```

4. Deploy to Modal:
```bash
# For simple REST API
modal deploy uroman_modal_simple.py

# For MCP server
modal deploy uroman_mcp_modal.py

# For production deployment
modal deploy uroman_modal_production.py
```

## Usage

Once deployed, you'll get an endpoint URL. You can send POST requests to it:

```bash
curl -X POST https://your-app-name--romanize-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -d '{"text": "Привет мир", "lang_code": "rus"}'
```

Response:
```json
{
  "original": "Привет мир",
  "romanized": "Privet mir",
  "lang_code": "rus"
}
```

## Why Modal instead of AWS Lambda?

- **No 15-minute timeout**: Uroman initialization can take time with all the Unicode data
- **Better cold starts**: Modal keeps containers warm more efficiently
- **Simpler deployment**: No SAM templates, no CloudFormation, just Python
- **Pay per second**: Only pay when your function is actually running

## Testing

Run the integration tests to ensure everything works:

```bash
cd .. && python -m pytest tests/test_comprehensive_suite.py -v
```

## Performance Notes

- First request (cold start): ~5-10 seconds (loading Unicode data)
- Subsequent requests: <100ms
- Container stays warm for 5 minutes after last request

## Cost Estimation

With Modal's free tier ($30/month credit):
- ~1 million romanization requests per month
- Or ~40 hours of continuous runtime

## Troubleshooting

If you get import errors, make sure the uroman directory structure is correct:
```
uroman/
├── modal-deployment/
│   ├── uroman_modal_simple.py
│   ├── uroman_mcp_modal.py
│   ├── uroman_modal_production.py
│   └── README.md
├── uroman/
│   ├── __init__.py
│   ├── uroman.py
│   └── data/
└── tests/
    └── test_comprehensive_suite.py
```
