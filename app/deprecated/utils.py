import boto3
import json 
from typing import List, Dict

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def send_to_llm(processed_query: str):
    try:
        response = bedrock.invoke_model(
            modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0", 
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    {
                        "role": "user",
                        "content": processed_query
                    }
                ],
                "max_tokens": 300,
            })
        )
        print(response)
        response_body = json.loads(response['body'].read())
        print(response_body)
        return response_body['content'][0]['text']
    except Exception as e:
        #raise HTTPException(status_code=500, detail=str(e))
        print(e)

query = 'how many calories in an apple. Return only an integer, no additional context'
print(send_to_llm(query))