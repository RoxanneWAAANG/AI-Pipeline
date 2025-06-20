# Project 2 -- AI Pipeline Orchestration

A serverless AI pipeline built on AWS that orchestrates conversational AI workflows using Step Functions, Lambda, and comprehensive monitoring.

## Overview

This project extends a basic chatbot implementation with sophisticated workflow orchestration, demonstrating enterprise-grade AI pipeline patterns including input analysis, response enhancement, and comprehensive logging.

## Architecture

The pipeline processes user requests through four orchestrated stages:
1. Input Analysis - Analyzes query complexity and characteristics
2. AI Processing - Generates responses using Amazon Bedrock
3. Response Enhancement - Adds metadata and formatting
4. Logging - Stores detailed execution records

## Prerequisites

- AWS CLI configured with appropriate permissions
- AWS SAM CLI installed
- Python 3.8+ with boto3
- Existing AWS Bedrock access

## Deployment

### Step 1: Clone and Setup
```bash
git clone https://github.com/RoxanneWAAANG/AI-Pipeline.git
cd AI-Pipeline
```

### Step 2: Deploy Pipeline
```bash
sam build --template pipeline-template.yaml
sam deploy --template pipeline-template.yaml --guided --stack-name ai-pipeline
```

### Step 3: Configure Monitoring
```bash
./create_dashboard.sh
```

## Usage

### API Endpoint
```
POST https://o77htsxjbd.execute-api.us-east-2.amazonaws.com/Prod/pipeline
Content-Type: application/json

{
  "message": "Your question here"
}
```

### Response Format
```json
{
  "execution_arn": "arn:aws:states:us-east-2:251761521792:execution:AIPipeline:...",
  "message": "Pipeline started successfully"
}
```

### Testing
```bash
curl -X POST https://o77htsxjbd.execute-api.us-east-2.amazonaws.com/Prod/pipeline \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain machine learning"}'
```

## Monitoring

- **CloudWatch Dashboard**: Real-time metrics and performance monitoring
- **Step Functions Console**: Visual workflow execution tracking
- **DynamoDB Logs**: Detailed execution records and analytics

## Project Structure

```
AI-Pipeline/
├── chatbot/                    # Original chatbot implementation
├── pipeline/                   # Pipeline components
│   ├── input_analyzer/         # Input analysis Lambda
│   ├── response_enhancer/      # Response enhancement Lambda
│   ├── pipeline_logger/        # Logging Lambda
│   └── trigger.py             # Pipeline trigger function
├── pipeline-template.yaml     # SAM deployment template
├── create_dashboard.sh        # Monitoring setup script
└── docs/                      # Documentation
    ├── ARCHITECTURE.md
    ├── MONITORING.md
    └── PIPELINE.md
```

## Key Features

- **Serverless Architecture**: Auto-scaling Lambda functions and Step Functions
- **Error Handling**: Comprehensive retry mechanisms with exponential backoff
- **Monitoring**: Real-time dashboards and detailed logging
- **Modularity**: Independent components for easy testing and maintenance
- **Cost Optimization**: Pay-per-request pricing model

## Development

### Running Tests
```bash
python -m pytest tests/ --cov=pipeline --cov-report=term
```

### Local Development
```bash
sam local start-api --template pipeline-template.yaml
```
