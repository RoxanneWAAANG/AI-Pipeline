import boto3
import json

cloudwatch = boto3.client('cloudwatch')

dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/StepFunctions", "ExecutionsSucceeded", "StateMachineArn", "arn:aws:states:us-east-2:251761521792:execution:AIPipeline:77520d5a-062d-4266-abb1-d66f12d8b9b5"],
                    [".", "ExecutionsFailed", ".", "."],
                    [".", "ExecutionTime", ".", "."]
                ],
                "period": 300,
                "stat": "Sum",
                "region": "us-east-2",
                "title": "Pipeline Execution Metrics"
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/Lambda", "Duration", "FunctionName", "InputAnalyzerFunction"],
                    [".", ".", ".", "ResponseEnhancerFunction"],
                    [".", ".", ".", "PipelineLoggerFunction"]
                ],
                "period": 300,
                "stat": "Average",
                "region": "us-east-2",
                "title": "Lambda Performance"
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='AIPipelineDashboard',
    DashboardBody=json.dumps(dashboard_body)
)