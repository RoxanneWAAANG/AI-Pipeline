import json
import re

def lambda_handler(event, context):
    """Analyze user input for complexity and intent"""
    user_message = event['message']
    
    # Simple analysis logic
    word_count = len(user_message.split())
    has_code = bool(re.search(r'```|`|\bcode\b|\bfunction\b', user_message, re.IGNORECASE))
    has_question = '?' in user_message
    is_complex = word_count > 20 or has_code
    
    analysis = {
        'word_count': word_count,
        'has_code': has_code,
        'has_question': has_question,
        'complexity': 'high' if is_complex else 'low',
        'estimated_tokens': word_count * 1.3  # rough estimate
    }
    
    # Pass through original event with analysis
    return {
        **event,
        'analysis': analysis,
        'timestamp': context.aws_request_id
    }