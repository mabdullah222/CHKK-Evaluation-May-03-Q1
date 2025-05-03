import json
import boto3
import csv
import uuid
import os
import base64
from io import StringIO
from botocore.exceptions import ClientError
import httpx

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

dynamo_table_name = 'Transactions'
sns_topic_arn = 'arn:aws:sns:ap-south-1:864981715346:CSVProcessingTopic'

groq_api_key = os.environ['GROQ_API_KEY']
groq_model = "llama3-70b-8192"
groq_api_url = "https://api.groq.com/openai/v1/chat/completions"

def lambda_handler(event, context):
    try:
        file_content_base64 = event['body']
        print(file_content_base64)
        file_content = base64.b64decode(file_content_base64)

        csv_data = StringIO(file_content.decode('utf-8'))
        reader = csv.DictReader(csv_data)
        rows = [row for row in reader]

        summary = generate_summary(rows)

        summary_id = str(uuid.uuid4())
        store_summary_in_dynamodb(summary_id, summary)
        publish_sns_event(summary_id, summary)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'File processed successfully', 'summary': summary})
        }

    except Exception as e:
        print(f"Error processing file: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal Server Error', 'error': str(e)})
        }

def generate_summary(csv_data):
    rows_str = "\n".join([json.dumps(row) for row in csv_data])
    prompt = f"""You are a helpful assistant. Summarize the following CSV transaction data in JSON format:

CSV Rows:
{rows_str}

Summary:"""
    return call_llm(prompt)

def call_llm(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": groq_model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that summarizes CSV transaction data."},
                {"role": "user", "content": prompt}
            ]
        }

        response = httpx.post(groq_api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"Error calling Groq LLM: {str(e)}")
        raise Exception("Failed to summarize CSV with LLM")

def store_summary_in_dynamodb(summary_id, summary):
    try:
        table = dynamodb.Table(dynamo_table_name)
        table.put_item(
            Item={
                'id': summary_id,
                'summaryData': summary,
                'timestamp': str(uuid.uuid4()),
            }
        )
    except ClientError as e:
        print(f"Error storing summary in DynamoDB: {e}")
        raise

def publish_sns_event(summary_id, summary):
    try:
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=json.dumps({'summaryId': summary_id, 'summary': summary}),
            Subject='CSV Summary Generated'
        )
    except ClientError as e:
        print(f"Error publishing SNS event: {e}")
        raise
