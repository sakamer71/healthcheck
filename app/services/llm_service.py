import boto3
import logging
#boto3.set_stream_logger(name='botocore', level=logging.DEBUG)
import json
from fastapi import HTTPException
from app.core.config import settings
import logging

model = settings.models['llm']['default']
model_region = settings.models['llm'][model]['model_region']
model_id = settings.models['llm'][model]['model_id']
max_tokens = settings.models['llm'][model]['max_tokens']
print(settings.nutrition)


bedrock = boto3.client('bedrock-runtime', region_name=model_region)

async def parse_query(query:str) -> str:
    return f"For the following meal, tell me the nutritional value for each category of {settings.nutrition}: {query}  Where possible, return integer values. Respond only with json, no additional text."

async def format_response(llm_response: str) -> dict:
    try:
        response_json = json.loads(llm_response)
        return response_json
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON response from LLM")

async def send_to_llm(processed_query: str) -> str:
    try:
        response = bedrock.converse(
            modelId = model_id,
            messages=[
                    {
                    "role": "user",
                    "content": [{'text':processed_query}]
                    }
            ]
        )

        print(f'MY RESPONSE IS {response}')  
        print(type(response))      
        response_body = response['output']['message']
        print(response_body)
        return response_body['content'][0]['text']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))