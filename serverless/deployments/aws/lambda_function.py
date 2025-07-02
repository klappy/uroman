"""
AWS Lambda handler for uroman using multi-cloud architecture
"""

import sys
from pathlib import Path

# Add serverless to path (Lambda layers will include these)
sys.path.insert(0, '/opt/python')

from serverless.adapters.aws_lambda_adapter import AWSLambdaAdapter

# Create adapter instance
adapter = AWSLambdaAdapter()

# Create Lambda handlers
lambda_handler = adapter.create_lambda_handler("http")
mcp_handler = adapter.create_lambda_handler("mcp")

# You can deploy these as separate Lambda functions or use 
# API Gateway routes to direct to different handlers
