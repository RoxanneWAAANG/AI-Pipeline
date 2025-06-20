import json
from datetime import datetime

def lambda_handler(event, context):
    """Enhanced response enhancer that handles different chatbot response formats"""
    
    try:
        # Get the response from your existing chatbot
        chatbot_response = event['chatbot_response']
        analysis = event['analysis']
        
        print(f"Chatbot response format: {chatbot_response}")  # Debug log
        
        # Handle different possible response formats from your chatbot
        if isinstance(chatbot_response, dict):
            # Case 1: Direct response object
            if 'reply' in chatbot_response:
                reply = chatbot_response['reply']
                metadata = chatbot_response.get('metadata', {})
            elif 'body' in chatbot_response:
                # Case 2: API Gateway format
                body = json.loads(chatbot_response['body']) if isinstance(chatbot_response['body'], str) else chatbot_response['body']
                reply = body.get('reply', body.get('message', body.get('response', str(body))))
                metadata = body.get('metadata', {})
            elif 'message' in chatbot_response:
                # Case 3: Simple message format
                reply = chatbot_response['message']
                metadata = chatbot_response.get('metadata', {})
            else:
                # Case 4: Unknown format, convert to string
                reply = str(chatbot_response)
                metadata = {}
        elif isinstance(chatbot_response, str):
            # Case 5: String response
            try:
                parsed = json.loads(chatbot_response)
                reply = parsed.get('reply', parsed.get('message', chatbot_response))
                metadata = parsed.get('metadata', {})
            except:
                reply = chatbot_response
                metadata = {}
        else:
            # Case 6: Fallback
            reply = str(chatbot_response)
            metadata = {}
        
        # Create enhanced response
        enhanced_response = {
            'reply': reply,
            'metadata': {
                **metadata,
                'pipeline_id': context.aws_request_id,
                'processing_time': datetime.utcnow().isoformat(),
                'input_analysis': analysis,
                'enhancement_applied': True,
                'original_response_type': type(chatbot_response).__name__
            }
        }
        
        # Add helpful formatting for complex queries
        if analysis['complexity'] == 'high':
            enhanced_response['metadata']['complexity_note'] = "This was identified as a complex query"
        
        return {
            **event,
            'enhanced_response': enhanced_response
        }
        
    except Exception as e:
        print(f"Error in response enhancer: {str(e)}")
        # Fallback response
        return {
            **event,
            'enhanced_response': {
                'reply': f"Response processing error: {str(e)}",
                'metadata': {
                    'pipeline_id': context.aws_request_id,
                    'processing_time': datetime.utcnow().isoformat(),
                    'error': True,
                    'error_message': str(e),
                    'original_response': str(event.get('chatbot_response', 'No response'))
                }
            }
        }