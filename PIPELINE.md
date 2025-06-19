# AI Pipeline Documentation

## Pipeline Overview

The AI Pipeline orchestrates conversational AI workflows through four sequential stages, transforming user input into enhanced responses with comprehensive logging and monitoring.

## Pipeline Flow

```
User Request → Input Analysis → AI Processing → Response Enhancement → Logging → Response
```

## Stage Definitions

### Stage 1: Input Analysis
**Function**: `InputAnalyzerFunction`  
**Purpose**: Analyze user input characteristics and complexity

#### Input Schema
```json
{
  "message": "string"
}
```

#### Processing Logic
- **Word Count**: Count total words in message
- **Code Detection**: Regex pattern matching for code blocks
- **Question Detection**: Identify interrogative patterns
- **Complexity Classification**: Binary classification (high/low)

#### Output Schema
```json
{
  "message": "original input",
  "analysis": {
    "word_count": "number",
    "has_code": "boolean",
    "has_question": "boolean",
    "complexity": "high|low",
    "estimated_tokens": "number"
  },
  "timestamp": "execution_id"
}
```

### Stage 2: AI Processing
**Function**: Existing Chatbot Integration  
**Purpose**: Generate AI response using Amazon Bedrock

#### Integration Method
- **Type**: Lambda Invoke Task
- **Target**: `serverless-chat-ChatbotFunction`
- **Payload**: Complete pipeline event

#### Processing
- Maintains existing chatbot functionality
- Preserves conversation history support
- Utilizes Amazon Bedrock Claude model
- Implements rate limiting and validation

#### Output Enhancement
```json
{
  "chatbot_response": {
    "reply": "string",
    "metadata": {
      "conversation_id": "string",
      "response_time_ms": "number",
      "estimated_tokens": "object"
    }
  }
}
```

### Stage 3: Response Enhancement
**Function**: `ResponseEnhancerFunction`  
**Purpose**: Enrich response with metadata and formatting

#### Enhancement Logic
- **Metadata Addition**: Pipeline tracking information
- **Timestamp Injection**: Processing time records
- **Complexity Handling**: Special formatting for complex queries
- **Performance Metrics**: Execution time tracking

#### Output Schema
```json
{
  "enhanced_response": {
    "reply": "string",
    "metadata": {
      "pipeline_id": "string",
      "processing_time": "ISO-8601",
      "input_analysis": "object",
      "enhancement_applied": "boolean",
      "complexity_note": "string (optional)"
    }
  }
}
```

### Stage 4: Logging
**Function**: `PipelineLoggerFunction`  
**Purpose**: Store execution records and metrics

#### Logging Logic
- **DynamoDB Storage**: Persistent execution records
- **Performance Metrics**: Timing and resource usage
- **Error Handling**: Graceful failure logging
- **Status Tracking**: Success/failure indicators

#### Log Record Schema
```json
{
  "pipeline_id": "string",
  "timestamp": "ISO-8601",
  "user_message": "string",
  "analysis": "object",
  "final_response": "object",
  "execution_time_ms": "number",
  "status": "SUCCESS|FAILED"
}
```

## Data Flow

### Request Processing
1. **API Gateway**: Receives HTTP POST request
2. **Pipeline Trigger**: Initiates Step Functions execution
3. **State Machine**: Orchestrates sequential processing
4. **Lambda Functions**: Execute individual processing stages
5. **DynamoDB**: Stores execution results
6. **Response**: Returns execution acknowledgment

### Data Transformation
```
Raw Input → Analysis Metadata → AI Response → Enhanced Response → Logged Record
```

### State Transitions
```
Start → AnalyzeInput → CallExistingChatbot → EnhanceResponse → LogResults → End
```

## Error Handling

### Retry Configuration

#### Per-State Retry Policy
```json
{
  "Retry": [
    {
      "ErrorEquals": ["States.ALL"],
      "IntervalSeconds": 2,
      "MaxAttempts": 3,
      "BackoffRate": 2
    }
  ]
}
```

#### Bedrock-Specific Retries
```json
{
  "Retry": [
    {
      "ErrorEquals": ["Bedrock.RuntimeException", "Bedrock.ClientException"],
      "IntervalSeconds": 2,
      "MaxAttempts": 3,
      "BackoffRate": 2
    }
  ]
}
```

### Error Recovery
- **Catch Blocks**: Capture all unhandled errors
- **Graceful Degradation**: Continue pipeline on non-critical failures
- **Error Logging**: All errors stored in DynamoDB
- **Status Tracking**: Failed executions marked appropriately

## Performance Characteristics

### Execution Metrics
- **Average Duration**: 3-5 seconds end-to-end
- **Stage Breakdown**:
  - Input Analysis: 100-500ms
  - AI Processing: 2-3 seconds
  - Response Enhancement: 50-200ms
  - Logging: 100-300ms

### Throughput Limits
- **Concurrent Executions**: 1000 (configurable)
- **API Gateway**: 10,000 RPS
- **Step Functions**: No built-in limits
- **Lambda**: Per-function concurrency limits

### Resource Utilization
- **Memory**: 128 MB per function (optimized)
- **CPU**: Auto-allocated based on memory
- **Storage**: DynamoDB on-demand scaling

## Configuration Management

### Environment Variables

#### Pipeline Functions
```yaml
InputAnalyzerFunction:
  Environment:
    Variables: {}

ResponseEnhancerFunction:
  Environment:
    Variables: {}

PipelineLoggerFunction:
  Environment:
    Variables:
      PIPELINE_LOG_TABLE: PipelineLogs
```

#### Existing Chatbot Integration
```yaml
ChatbotFunction:
  Environment:
    Variables:
      BEDROCK_MODEL_ID: anthropic.claude-3-sonnet-20240229-v1:0
```

### IAM Permissions

#### Step Functions Execution Role
```yaml
Policies:
  - PolicyName: StepFunctionsExecutionPolicy
    PolicyDocument:
      Statement:
        - Effect: Allow
          Action:
            - lambda:InvokeFunction
          Resource: '*'
```

#### Lambda Execution Roles
```yaml
PipelineLoggerFunction:
  Policies:
    - DynamoDBWritePolicy:
        TableName: !Ref PipelineLogTable
```

## Pipeline Operations

### Execution Commands

#### Start Pipeline Execution
```bash
curl -X POST https://o77htsxjbd.execute-api.us-east-2.amazonaws.com/Prod/pipeline \
  -H "Content-Type: application/json" \
  -d '{"message": "Your question here"}'
```

#### Check Execution Status
```bash
aws stepfunctions describe-execution \
  --execution-arn "arn:aws:states:us-east-2:251761521792:execution:AIPipeline:EXECUTION_ID"
```

#### List Recent Executions
```bash
aws stepfunctions list-executions \
  --state-machine-arn $(aws stepfunctions list-state-machines \
    --query 'stateMachines[?name==`AIPipeline`].stateMachineArn' \
    --output text) \
  --max-items 10
```

### Debugging Procedures

#### Failed Execution Analysis
1. **Step Functions Console**: Visual execution graph
2. **CloudWatch Logs**: Detailed error messages
3. **DynamoDB Query**: Execution context and metadata
4. **Lambda Metrics**: Function-specific performance data

#### Common Debug Scenarios
- **Input Analysis Failures**: Invalid input format
- **Chatbot Integration Issues**: Bedrock API errors
- **Enhancement Failures**: Metadata processing errors
- **Logging Failures**: DynamoDB permission issues

## Testing Strategy

### Unit Testing
```bash
# Test individual Lambda functions
python -m pytest tests/test_input_analyzer.py
python -m pytest tests/test_response_enhancer.py
python -m pytest tests/test_pipeline_logger.py
```

### Integration Testing
```bash
# End-to-end pipeline test
./test_pipeline.sh
```

### Load Testing
```bash
# Concurrent execution test
for i in {1..10}; do
  curl -X POST $API_ENDPOINT \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Test message $i\"}" &
done
```

## Deployment Pipeline

### Infrastructure as Code
- **Template**: `pipeline-template.yaml`
- **Framework**: AWS SAM
- **Deployment**: CloudFormation stack

### Deployment Commands
```bash
# Build artifacts
sam build --template pipeline-template.yaml

# Deploy to AWS
sam deploy --template pipeline-template.yaml \
  --guided \
  --stack-name ai-pipeline

# Validate deployment
aws stepfunctions list-state-machines \
  --query 'stateMachines[?name==`AIPipeline`]'
```

### Rollback Procedures
```bash
# Rollback to previous version
aws cloudformation update-stack \
  --stack-name ai-pipeline \
  --use-previous-template

# Monitor rollback status
aws cloudformation describe-stacks \
  --stack-name ai-pipeline \
  --query 'Stacks[0].StackStatus'
```