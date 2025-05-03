from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_iam as iam,
)
from constructs import Construct

class SummarizeCsvServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Existing Lambda ARN
        lambda_function_arn = "arn:aws:lambda:ap-south-1:864981715346:function:summarizing-handler"
        lambda_function = _lambda.Function.from_function_arn(self, "ImportedFunction", lambda_function_arn)

        # DynamoDB Table
        table = dynamodb.Table(
            self, "TransactionsTable",
            table_name="Transactions",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING)
        )

        # Allow Lambda to write to DynamoDB
        table.grant_write_data(lambda_function)

        # Allow Lambda to publish to SNS
        lambda_function.add_to_role_policy(iam.PolicyStatement(
            actions=["sns:Publish"],
            resources=["arn:aws:sns:ap-south-1:864981715346:CSVProcessingTopic"]
        ))

        # API Gateway
        api = apigateway.RestApi(self, "SummarizeCSVApi",
            rest_api_name="SummarizeCSVApi",
            description="API to upload and summarize CSV files",
            binary_media_types=["application/octet-stream", "text/csv"]
        )

        summarize = api.root.add_resource("summarize")

        summarize.add_method("POST",
            apigateway.LambdaIntegration(lambda_function, proxy=True),
            method_responses=[
                {
                    'statusCode': '200'
                },
                {
                    'statusCode': '500'
                }
            ]
        )
