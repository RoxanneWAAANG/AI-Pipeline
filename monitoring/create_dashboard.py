#!/usr/bin/env python3
"""
Create CloudWatch Dashboard for AI Pipeline Monitoring
"""

import boto3
import json

def create_monitoring_dashboard():
    cloudwatch = boto3.client('cloudwatch')
    
    # Get your Step Functions state machine ARN
    # Replace with your actual ARN
    state_machine_arn = "arn:aws:states:us-east-2:251761521792:stateMachine:AIPipeline"
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0,
                "y": 0,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/StepFunctions", "ExecutionsSucceeded", "StateMachineArn", state_machine_arn],
                        [".", "ExecutionsFailed", ".", "."],
                        [".", "ExecutionsAborted", ".", "."],
                        [".", "ExecutionsTimedOut", ".", "."]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-2",
                    "title": "Pipeline Execution Status",
                    "period": 300,
                    "stat": "Sum"
                }
            },
            {
                "type": "metric",
                "x": 12,
                "y": 0,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/StepFunctions", "ExecutionTime", "StateMachineArn", state_machine_arn]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-2",
                    "title": "Pipeline Execution Time",
                    "period": 300,
                    "stat": "Average"
                }
            },
            {
                "type": "metric",
                "x": 0,
                "y": 6,
                "width": 24,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/Lambda", "Duration", "FunctionName", "ai-pipeline-InputAnalyzerFunction"],
                        [".", ".", ".", "ai-pipeline-ResponseEnhancerFunction"],
                        [".", ".", ".", "ai-pipeline-PipelineLoggerFunction"],
                        [".", ".", ".", "ai-pipeline-PipelineFunction"]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-2",
                    "title": "Lambda Function Performance (Duration)",
                    "period": 300,
                    "stat": "Average"
                }
            },
            {
                "type": "metric",
                "x": 0,
                "y": 12,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/Lambda", "Invocations", "FunctionName", "ai-pipeline-InputAnalyzerFunction"],
                        [".", ".", ".", "ai-pipeline-ResponseEnhancerFunction"],
                        [".", ".", ".", "ai-pipeline-PipelineLoggerFunction"],
                        [".", ".", ".", "ai-pipeline-PipelineFunction"]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-2",
                    "title": "Lambda Invocations",
                    "period": 300,
                    "stat": "Sum"
                }
            },
            {
                "type": "metric",
                "x": 12,
                "y": 12,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/Lambda", "Errors", "FunctionName", "ai-pipeline-InputAnalyzerFunction"],
                        [".", ".", ".", "ai-pipeline-ResponseEnhancerFunction"],
                        [".", ".", ".", "ai-pipeline-PipelineLoggerFunction"],
                        [".", ".", ".", "ai-pipeline-PipelineFunction"]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-2",
                    "title": "Lambda Errors",
                    "period": 300,
                    "stat": "Sum"
                }
            }
        ]
    }
    
    response = cloudwatch.put_dashboard(
        DashboardName='AIPipelineDashboard',
        DashboardBody=json.dumps(dashboard_body)
    )
    print("Dashboard created successfully!")
    print(f"Dashboard URL: https://us-east-2.console.aws.amazon.com/cloudwatch/home?region=us-east-2#dashboards:name=AIPipelineDashboard")
    return response

if __name__ == "__main__":
    create_monitoring_dashboard()