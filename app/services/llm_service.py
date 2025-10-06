from app import api
import boto3
import logging
import json
from fastapi import HTTPException
from app.core.config import settings
from openai import AzureOpenAI

## get parameter from ssm parameter store
def get_ssm_parameter(ssm, parameter):
    #result = ssm.get_parameter(Name=parameter)
    result = ssm.get_parameters(Names=[parameter])
    #return result['Parameter']['Value']
    return result['Parameters'][0]['Value']

# Azure OpenAI client setup
def get_openai_client():
    try:
        ssm = boto3.client('ssm', region_name='us-east-2')
        model = settings.models['llm']['default']
        endpoint = settings.models['llm'][model]['model_endpoint']
        api_key = settings.models['llm'][model]['model_api_key']    
        client = AzureOpenAI(
            azure_endpoint = get_ssm_parameter(ssm, endpoint),
            api_key = get_ssm_parameter(ssm, api_key),
            api_version="2024-02-15-preview"
        )
        return client
    except Exception as e:
        logging.error(f"Error creating OpenAI client: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# AWS Bedrock client setup
def get_bedrock_client(model, model_region):
    try:
        client = boto3.client('bedrock-runtime', region_name=model_region)
        return client
    except Exception as e:
        logging.error(f"Error creating Bedrock client: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def format_response(llm_response: str) -> dict:
    try:
        cleaned_response = llm_response.strip()
        if cleaned_response.startswith('```') and cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[3:-3].strip()
            if cleaned_response.startswith('json\n'):
                cleaned_response = cleaned_response[5:].strip()
        
        try:
            response_json = json.loads(cleaned_response)
            return response_json
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON: {cleaned_response}")
            logging.error(f"JSON error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Invalid JSON response from LLM: {str(e)}")
        
    except Exception as e:
        logging.error(f"Error in format_response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def send_to_llm(processed_query: str) -> str:
    try:
        model = settings.models['llm']['default']
        model_region = settings.models['llm'][model]['model_region']
        if 'gpt' in model.lower():
            client = get_openai_client()
            response = client.chat.completions.create(
                model=settings.models['llm'][model]['model_deployment_name'],
                messages=[{"role": "user", "content": processed_query}],
                max_tokens=4096
            )
            response_message = json.loads(response.model_dump_json())["choices"][0]["message"]["content"].strip()
        else:
            client = get_bedrock_client(model, model_region)
            response = client.converse(
                modelId = settings.models['llm'][model]['model_id'],
                messages=[
                        {
                        "role": "user",
                        "content": [{'text':processed_query}]
                        }
                ]
            )
            response_body = response['output']['message']
            response_message = response_body['content'][0]['text']
        return response_message
    except Exception as e:
        logging.error(f"Error in send_to_llm: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
