from fastapi import APIRouter
from app.services import llm_service

router = APIRouter()

@router.get("/api/calorie_count/{query:path}")
async def calorie_count(query: str):
    processed_query = await llm_service.parse_query(query)
    print(f'MY processed query is {processed_query}')
    llm_response = await llm_service.send_to_llm(processed_query)
    formatted_response = await llm_service.format_response(llm_response)
    return formatted_response
