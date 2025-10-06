from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from app.services.llm_service import send_to_llm, format_response
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ProfileData(BaseModel):
    age: int
    heightCm: float
    weightKg: float
    targetWeightKg: float
    targetDate: str
    activityLevel: str
    gender: Optional[str] = "unknown"

async def create_rda_prompt(profile: ProfileData) -> str:
    try:
        target_date = datetime.strptime(profile.targetDate, "%Y-%m-%d")
        days_until_target = (target_date - datetime.now()).days
        
        return f"""Calculate RDA. Age: {profile.age}y, Height: {profile.heightCm}cm, Weight: {round(profile.weightKg, 1)}kg, Target: {round(profile.targetWeightKg, 1)}kg in {days_until_target} days, Activity: {profile.activityLevel}. 

Respond with ONLY a valid JSON object in this EXACT format, with NO additional text or formatting:
{{"calories": 2000, "protein": 50, "fat": 70, "fiber": 25, "carbohydrates": 300}}

Replace the example numbers with calculated values based on the profile."""

    except Exception as e:
        logger.error(f"Error creating RDA prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-rda")
async def calculate_rda(profile: ProfileData) -> Dict:
    try:
        # Create a concise prompt that works with the existing LLM service
        prompt = await create_rda_prompt(profile)
        logger.info(f"Generated prompt: {prompt}")
        
        # Send to LLM service using the global instance
        llm_response = await send_to_llm(prompt)
        logger.info(f"LLM response: {llm_response}")
        
        # Parse the response
        formatted_response = await format_response(llm_response)
        logger.info(f"Formatted response: {formatted_response}")
        
        # Validate required fields
        required_fields = ["calories", "protein", "fat", "fiber", "carbohydrates"]
        for field in required_fields:
            if field not in formatted_response:
                raise ValueError(f"Missing required field: {field}")
                
        return formatted_response

    except Exception as e:
        logger.error(f"Error in calculate_rda: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
