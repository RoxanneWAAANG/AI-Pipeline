# Monitoring and Observability

## Overview

Comprehensive monitoring strategy using AWS CloudWatch, Step Functions insights, and DynamoDB logging to ensure pipeline reliability and performance visibility.

## Monitoring Stack

### Primary Tools
- **CloudWatch**: Metrics, logs, and dashboards
- **Step Functions Console**: Workflow execution tracking
- **DynamoDB**: Detailed execution logging
- **AWS X-Ray**: Distributed tracing (optional)

## CloudWatch Dashboard

### Dashboard URL
```
https://us-east-2.console.aws.amazon.com/cloudwatch/home?region=us-east-2#dashboards:name=AIPipelineDashboard
```

### Dashboard Setup
```bash
# Automated dashboard creation
./create_dashboard.sh
```

### Dashboard Components

#### 1. Pipeline Execution Status
- **Metrics**: ExecutionsSucceeded, ExecutionsFailed, ExecutionsAborted, ExecutionsTimedOut
- **Namespace**: AWS/StepFunctions
- **Visualization**: Time series chart
- **Period**: 5 minutes

#### 2. Pipeline Execution Time
- **Metric**: ExecutionTime
- **Namespace**: AWS/StepFunctions
- **Visualization**: Time series chart
- **Statistic**: Average

#### 3. Lambda Function Performance
- **Metrics**: Duration for all pipeline functions
- **Functions Monitored**:
  - InputAnalyzerFunction
  - ResponseEnhancerFunction
  - PipelineLoggerFunction
  - PipelineFunction
- **Visualization**: Multi-line time series

#### 4. Lambda Invocation Metrics
- **Metrics**: Invocations, Errors
- **Namespace**: AWS/Lambda
- **Visualization**: Time series chart

## Key Metrics

### Step Functions Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| ExecutionsSucceeded | Successful pipeline runs | N/A |
| ExecutionsFailed | Failed pipeline runs | > 5% of total |
| ExecutionsAborted | Manually aborted runs | > 1% of total |
| ExecutionTime | End-to-end execution time | > 30 seconds |

### Lambda Metrics

| Function | Metric | Normal Range | Alert Threshold |
|----------|--------|--------------|-----------------|
| InputAnalyzer | Duration | 100-500ms | > 2 seconds |
| ResponseEnhancer | Duration | 50-200ms | > 1 second |
| PipelineLogger | Duration | 100-300ms | > 2 seconds |
| All Functions | Errors | 0 | > 5 in 5 minutes |

### DynamoDB Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| ConsumedReadCapacityUnits | Read operations | Monitor for scaling |
| ConsumedWriteCapacityUnits | Write operations | Monitor for scaling |
| ThrottledRequests | Rate limiting events | > 0 |

## Logging Strategy

### CloudWatch Log Groups

```
/aws/lambda/ai-pipeline-InputAnalyzerFunction
/aws/lambda/ai-pipeline-ResponseEnhancerFunction
/aws/lambda/ai-pipeline-PipelineLoggerFunction
/aws/lambda/ai-pipeline-PipelineFunction
/aws/stepfunctions/AIPipeline
```

### Log Analysis Commands

#### View Recent Lambda Logs
```bash
# Input Analyzer logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/ai-pipeline-InputAnalyzerFunction \
  --start-time $(date -d '1 hour ago' +%s)000

# Pipeline execution logs
aws logs filter-log-events \
  --log-group-name /aws/stepfunctions/AIPipeline \
  --start-time $(date -d '1 hour ago' +%s)000
```

#### Search for Errors
```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/ai-pipeline-InputAnalyzerFunction \
  --filter-pattern "ERROR" \
  --start-time $(date -d '24 hours ago' +%s)000
```

## DynamoDB Logging

### Pipeline Execution Records

#### Query Recent Executions
```bash
aws dynamodb scan \
  --table-name PipelineLogs \
  --filter-expression "#ts > :timestamp" \
  --expression-attribute-names '{"#ts": "timestamp"}' \
  --expression-attribute-values '{":timestamp": {"S": "2024-01-01T00:00:00Z"}}'
```

#### Query Specific Execution
```bash
aws dynamodb get-item \
  --table-name PipelineLogs \
  --key '{"pipeline_id": {"S": "YOUR_EXECUTION_ID"}}'
```

### Log Schema
```json
{
  "pipeline_id": "uuid",
  "timestamp": "ISO-8601",
  "user_message": "string",
  "analysis": {
    "word_count": "number",
    "complexity": "high|low",
    "has_code": "boolean",
    "has_question": "boolean"
  },
  "final_response": {
    "reply": "string",
    "metadata": "object"
  },
  "execution_time_ms": "number",
  "status": "SUCCESS|FAILED"
}
```

## Alerting Configuration

### CloudWatch Alarms

#### High Error Rate Alarm
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "AIPipeline-HighErrorRate" \
  --alarm-description "Pipeline error rate exceeds 5%" \
  --metric-name ExecutionsFailed \
  --namespace AWS/StepFunctions \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

#### High Latency Alarm
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "AIPipeline-HighLatency" \
  --alarm-description "Pipeline execution time exceeds 30 seconds" \
  --metric-name ExecutionTime \
  --namespace AWS/StepFunctions \
  --statistic Average \
  --period 300 \
  --threshold 30000 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

### SNS Integration
```bash
# Create SNS topic for alerts
aws sns create-topic --name AIPipelineAlerts

# Subscribe email to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-2:ACCOUNT:AIPipelineAlerts \
  --protocol email \
  --notification-endpoint your-email@example.com
```

## Performance Monitoring

### Baseline Metrics
- **Average Execution Time**: 3-5 seconds
- **Success Rate**: > 95%
- **Lambda Duration**: < 2 seconds per function
- **DynamoDB Latency**: < 100ms

### Performance Analysis Queries

#### Execution Time Trends
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/StepFunctions \
  --metric-name ExecutionTime \
  --start-time $(date -d '24 hours ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 3600 \
  --statistics Average,Maximum
```

#### Error Rate Analysis
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/StepFunctions \
  --metric-name ExecutionsFailed \
  --start-time $(date -d '24 hours ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 3600 \
  --statistics Sum
```

## Operational Procedures

### Daily Health Check
1. Check CloudWatch dashboard for anomalies
2. Review error logs for any failures
3. Verify DynamoDB write operations
4. Monitor execution time trends

### Weekly Review
1. Analyze performance trends
2. Review cost metrics
3. Check for capacity planning needs
4. Update alert thresholds if needed

### Incident Response
1. Check Step Functions console for failed executions
2. Review CloudWatch logs for error details
3. Query DynamoDB for execution context
4. Escalate to development team if needed

## Troubleshooting Guide

### Common Issues

#### Pipeline Execution Failures
1. Check Step Functions execution details
2. Review individual Lambda function logs
3. Verify IAM permissions
4. Check Bedrock API quotas

#### High Latency
1. Monitor Lambda cold starts
2. Check DynamoDB throttling
3. Analyze Bedrock response times
4. Review network connectivity

#### Missing Logs
1. Verify DynamoDB table permissions
2. Check Lambda execution role
3. Review CloudWatch log retention
4. Validate log group configurations

### Diagnostic Commands
```bash
# Check pipeline health
aws stepfunctions list-executions \
  --state-machine-arn $(aws stepfunctions list-state-machines \
    --query 'stateMachines[?name==`AIPipeline`].stateMachineArn' \
    --output text) \
  --status-filter FAILED

# Recent errors
aws logs filter-log-events \
  --log-group-name /aws/stepfunctions/AIPipeline \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000
```