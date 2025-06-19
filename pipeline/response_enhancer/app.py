import json
from datetime import datetime

def lambda_handler(event, context):
    """Enhance the chatbot response with metadata and formatting"""
    
    # Get the response from your existing chatbot
    chatbot_response = event['chatbot_response']
    analysis = event['analysis']
    
    # Add enhancements based on analysis
    enhanced_response = {
        'reply': chatbot_response['reply'],
        'metadata': {
            **chatbot_response.get('metadata', {}),
            'pipeline_id': context.aws_request_id,
            'processing_time': datetime.utcnow().isoformat(),
            'input_analysis': analysis,
            'enhancement_applied': True
        }
    }
    
    # Add helpful formatting for complex queries
    if analysis['complexity'] == 'high':
        enhanced_response['metadata']['complexity_note'] = "This was identified as a complex query"
    
    return {
        **event,
        'enhanced_response': enhanced_response
    }