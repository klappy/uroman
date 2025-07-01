"""
AWS Lambda function for uroman romanization service
"""

import json
import uroman as ur

# Initialize uroman outside handler for reuse across invocations
uroman_instance = None

def get_uroman():
    """Get or create uroman instance"""
    global uroman_instance
    if uroman_instance is None:
        uroman_instance = ur.Uroman()
    return uroman_instance

def lambda_handler(event, context):
    """
    Lambda handler for romanization requests
    
    Expected event format:
    {
        "text": "Text to romanize",
        "language": "optional 3-letter language code",
        "format": "str|edges|alts|lattice" (optional, default: str)
    }
    """
    try:
        # Parse input
        body = json.loads(event['body']) if 'body' in event else event
        
        text = body.get('text', '')
        language = body.get('language', None)
        format_str = body.get('format', 'str')
        
        # Map format string to RomFormat enum
        format_map = {
            'str': ur.RomFormat.STR,
            'edges': ur.RomFormat.EDGES,
            'alts': ur.RomFormat.ALTS,
            'lattice': ur.RomFormat.LATTICE
        }
        rom_format = format_map.get(format_str, ur.RomFormat.STR)
        
        # Get uroman instance
        uroman = get_uroman()
        
        # Romanize
        result = uroman.romanize_string(text, lcode=language, rom_format=rom_format)
        
        # Format response based on output type
        if isinstance(result, str):
            response_data = {
                'original': text,
                'romanized': result,
                'format': format_str
            }
        else:
            # For edge/lattice formats, convert to JSON-serializable format
            response_data = {
                'original': text,
                'romanized': [json.loads(edge.json()) for edge in result],
                'format': format_str
            }
        
        if language:
            response_data['language'] = language
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to romanize text'
            })
        }

# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        'text': 'Привет мир',
        'language': 'rus'
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
