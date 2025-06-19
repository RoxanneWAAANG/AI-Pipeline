# System Architecture

## Overview

The AI Pipeline implements a serverless microservices architecture using AWS Step Functions for workflow orchestration, Lambda for compute, and managed services for storage and monitoring.

## System Design

### High-Level Architecture

```
Internet → API Gateway → Lambda Trigger → Step Functions → [4 Lambda Stages] → DynamoDB
                                                ↓
                                        CloudWatch Monitoring
```

### Component Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │───▶│ Pipeline Trigger│───▶│ Step Functions  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌────────────────────────────────┼────────────────────────────────┐
                       ▼                                ▼                                ▼
           ┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
           │ Input Analyzer  │              │Response Enhancer│              │Pipeline Logger  │
           └─────────────────┘              └─────────────────┘              └─────────────────┘
                       │                                │                                │
                       ▼                                ▼                                ▼
           ┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
           │Existing Chatbot │              │   Metadata      │              │   DynamoDB      │
           │   (Bedrock)     │              │  Enhancement    │              │     Logs        │
           └─────────────────┘              └─────────────────┘              └─────────────────┘
```

## Core Components

### 1. API Gateway
- **Purpose**: HTTP API endpoint for pipeline invocation
- **Configuration**: POST method with CORS enabled
- **Security**: IAM-based authentication
- **Endpoint**: `/pipeline`

### 2. Step Functions State Machine

#### State Definition
```json
{
  "StartAt": "AnalyzeInput",
  "States": {
    "AnalyzeInput": {
      "Type": "Task",
      "Resource": "InputAnalyzerFunction.Arn",
      "Next": "CallExistingChatbot"
    },
    "CallExistingChatbot": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Next": "EnhanceResponse"
    },
    "EnhanceResponse": {
      "Type": "Task",
      "Resource": "ResponseEnhancerFunction.Arn",
      "Next": "LogResults"
    },
    "LogResults": {
      "Type": "Task",
      "Resource": "PipelineLoggerFunction.Arn",
      "End": true
    }
  }
}
```

#### Error Handling Strategy
- **Retry Policy**: Exponential backoff (2-second intervals, 3 max attempts)
- **Catch Blocks**: All errors logged for debugging
- **Graceful Degradation**: Pipeline continues on non-critical failures

### 3. Lambda Functions

#### Input Analyzer Function
- **Runtime**: Python 3.9
- **Memory**: 128 MB
- **Timeout**: 30 seconds
- **Logic**: 
  - Word count analysis
  - Code detection (regex patterns)
  - Question identification
  - Complexity classification

#### Response Enhancer Function
- **Runtime**: Python 3.9
- **Memory**: 128 MB
- **Timeout**: 30 seconds
- **Logic**:
  - Metadata enrichment
  - Timestamp addition
  - Complexity-based formatting
  - Pipeline tracking information

#### Pipeline Logger Function
- **Runtime**: Python 3.9
- **Memory**: 128 MB
- **Timeout**: 30 seconds
- **Logic**:
  - DynamoDB record creation
  - Execution metrics capture
  - Error logging and tracking

### 4. Data Storage

#### DynamoDB Table: PipelineLogs
- **Primary Key**: pipeline_id (String)
- **Billing Mode**: Pay-per-request
- **Attributes**:
  - `pipeline_id`: Unique execution identifier
  - `timestamp`: Execution timestamp
  - `user_message`: Original user input
  - `analysis`: Input analysis results
  - `final_response`: Enhanced response data
  - `execution_time_ms`: Performance metrics
  - `status`: Execution status

## Design Decisions

### Why Step Functions?
1. **Visual Workflow**: Clear representation of pipeline stages
2. **Built-in Orchestration**: No custom coordination logic needed
3. **Error Handling**: Native retry and catch mechanisms
4. **Scaling**: Automatic handling of concurrent executions
5. **Monitoring**: Integrated CloudWatch metrics

### Why Separate Lambda Functions?
1. **Single Responsibility**: Each function has one clear purpose
2. **Independent Scaling**: Functions scale based on individual load
3. **Fault Isolation**: Failures in one stage don't affect others
4. **Testing**: Individual components easily unit tested
5. **Maintenance**: Separate deployment and versioning

### Why DynamoDB?
1. **Schema Flexibility**: JSON documents with varying structures
2. **Performance**: Single-digit millisecond latency
3. **Scaling**: Automatic capacity management
4. **Cost**: Pay-per-request pricing model
5. **Integration**: Native AWS service integration

## Performance Characteristics

### Latency
- **API Gateway**: < 10ms overhead
- **Step Functions**: < 100ms orchestration
- **Lambda Cold Start**: < 2 seconds (first invocation)
- **Lambda Warm**: < 50ms per function
- **DynamoDB**: < 10ms write operations

### Throughput
- **Concurrent Executions**: 1000 default (configurable)
- **API Gateway**: 10,000 requests per second
- **Step Functions**: Unlimited executions
- **DynamoDB**: On-demand scaling

### Resource Allocation
- **Memory**: 128 MB per Lambda (optimized for cost)
- **CPU**: Allocated proportionally to memory
- **Storage**: DynamoDB auto-scaling

## Security Model

### IAM Roles
1. **Step Functions Execution Role**
   - Lambda invocation permissions
   - CloudWatch logging access

2. **Lambda Execution Roles**
   - DynamoDB read/write permissions
   - CloudWatch logs access
   - Bedrock API access (existing chatbot)

### Network Security
- **VPC**: Not required (managed services)
- **Encryption**: TLS 1.2 for all API calls
- **Data Encryption**: DynamoDB encryption at rest

## Scalability Patterns

### Horizontal Scaling
- **Lambda**: Automatic concurrent execution scaling
- **DynamoDB**: On-demand capacity scaling
- **Step Functions**: Unlimited parallel executions

### Vertical Scaling
- **Memory**: Configurable Lambda memory allocation
- **CPU**: Automatically scaled with memory
- **Timeout**: Adjustable per function

## Monitoring Architecture

### CloudWatch Integration
- **Metrics**: Automatic collection for all services
- **Logs**: Centralized logging for all components
- **Alarms**: Configurable threshold monitoring
- **Dashboards**: Real-time visualization

### Custom Metrics
- **Pipeline Success Rate**: Successful executions / total executions
- **Average Execution Time**: End-to-end pipeline latency
- **Error Distribution**: Breakdown by component failure
- **Cost Tracking**: Per-execution cost analysis