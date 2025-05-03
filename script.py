import base64
import json
import sys
import os
import requests

API_ENDPOINT = "https://3f8aovnr28.execute-api.ap-south-1.amazonaws.com/v1/summarize"

def encode_file_to_base64(file_path):
    with open(file_path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')

def create_body_json(file_path, output_path='body.json'):
    if not os.path.isfile(file_path):
        print(f"❌ File not found: {file_path}")
        return None

    file_content_base64 = encode_file_to_base64(file_path)

    payload = {
        "body": file_content_base64,
        "isBase64Encoded": True
    }

    with open(output_path, 'w') as json_file:
        json.dump(payload, json_file, indent=4)

    print(f"✅ Successfully wrote Base64 payload to {output_path}")
    return payload

def invoke_api_gateway(payload):
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        print(f"📡 Invoked API Gateway. Status: {response.status_code}")
        print("🔽 Response:")
        print(response.text)
    except Exception as e:
        print(f"❌ Error calling API Gateway: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python generate_and_call.py <path_to_csv_file>")
    else:
        file_path = sys.argv[1]
        payload = create_body_json(file_path)
        if payload:
            invoke_api_gateway(payload)
