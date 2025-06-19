import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """Log pipeline execution with detailed metrics"""
    
    table_name = os.environ.get('PIPELINE_LOG_TABLE', 'PipelineLogs')
    table = dynamodb.Table(table_name)
    
    log_entry = {
        'pipeline_id': context.aws_request_id,
        'timestamp': datetime.utcnow().isoformat(),
        'user_message': event['message'],
        'analysis': event['analysis'],
        'final_response': event['enhanced_response'],
        'execution_time_ms': int(context.get_remaining_time_in_millis()),
        'status': 'SUCCESS'
    }
    
    try:
        table.put_item(Item=log_entry)
        print(f"Logged pipeline execution: {context.aws_request_id}")
    except Exception as e:
        print(f"Logging failed: {str(e)}")
    
    # Return the enhanced response for the user
    return event['enhanced_response']