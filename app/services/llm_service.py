from app import api
import boto3
import logging
#boto3.set_stream_logger(name='botocore', level=logging.DEBUG)
import json
from fastapi import HTTPException
from app.core.config import settings
import logging
from openai import AzureOpenAI





def initialize_llm_client(ssm, model, model_region):
    if 'gpt' in model.lower():
        llm = initialize_openai_client(ssm, model)      
    else:
        llm = boto3.client('bedrock-runtime', region_name=model_region)     
    return llm

def set_llm_response_template():
    if 'gpt' in model.lower():
        send_to_llm = azure_send_to_llm
    else:
        send_to_llm = aws_send_to_llm
    return send_to_llm

async def parse_query(query:str) -> str:
    #return f"For the following meal, tell me the nutritional value for each category of {settings.nutrition}: {query}  Where possible, return integer values. Respond only with json, no additional text."
    return f"For the following meal, tell me the nutritional value for each category of {settings.nutrition}: {query}  Where possible, return integer values. Respond **only** with the JSON object, without any additional text, code blocks, or formatting. Do not include language identifiers or backticks. Ensure the output is valid JSON."

async def format_response(llm_response: str) -> dict:
    try:
        response_json = json.loads(llm_response)
        return response_json
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON response from LLM")

async def aws_send_to_llm(processed_query: str) -> str:
    try:
        response = llm.converse(
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
    

async def azure_send_to_llm(processed_query: str) -> str:
    try:
        response = llm.chat.completions.create(
        model=settings.models['llm'][model]['model_deployment_name'],  # replace with the model deployment name of your o1-preview, or o1-mini model
        messages=[{"role": "user", "content": processed_query}],
        max_tokens=4096
    )
        response_message = json.loads(response.model_dump_json())["choices"][0]["message"]["content"].strip()
        #ss["messages"].append({"role": "assistant", "content": response_message})
        print(response_message)
        return response_message
        # response = llm.converse(
        #     modelId = model_id,
        #     messages=[
        #             {
        #             "role": "user",
        #             "content": [{'text':processed_query}]
        #             }
        #     ]
        # )

        # print(f'MY RESPONSE IS {response}')  
        # print(type(response))      
        # response_body = response['output']['message']
        # print(response_body)
        # return response_body['content'][0]['text']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

## get parameter from ssm parameter store
def get_ssm_parameter(ssm, parameter):
    result = ssm.get_parameter(Name=parameter)
    return result['Parameter']['Value']

# Azure OpenAI client setup
def initialize_openai_client(ssm, model):
    endpoint = settings.models['llm'][model]['model_endpoint']
    api_key = settings.models['llm'][model]['model_api_key']    
    client = AzureOpenAI(
        azure_endpoint = get_ssm_parameter(ssm, endpoint),
        api_key = get_ssm_parameter(ssm, api_key),
        api_version="2024-09-01-preview"
    )
    return client

#def main(query:str):
model = settings.models['llm']['default']
print(f'MY MODEL IS {model}')
model_region = settings.models['llm'][model]['model_region']
model_id = settings.models['llm'][model]['model_id']
max_tokens = settings.models['llm'][model]['max_tokens']
ssm = boto3.client('ssm', region_name='us-east-2')
#llm = initialize_llm_client(ssm, model_id, model_region)
llm = initialize_llm_client(ssm, model, model_region)
print('MY LLM IS')
print(llm)
send_to_llm = set_llm_response_template()


print(settings.nutrition)
