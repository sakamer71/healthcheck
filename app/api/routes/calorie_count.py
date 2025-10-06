from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from app.services import llm_service, db_utils
from app.services.image_service import search_meal_image
from datetime import date
from typing import Optional
import datetime
import time
import logging
import json
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

def normalize_meal_data(data: dict) -> dict:
    """Normalize field names and ensure all required fields are present"""
    field_mapping = {
        'total fat': 'total_fat',
        'total_fat': 'total_fat',
        'carbs': 'carbohydrates',
        'carbohydrates': 'carbohydrates',
        'serving size': 'serving_size'
    }
    
    normalized = {}
    
    # Copy all fields, normalizing known fields
    for key, value in data.items():
        normalized_key = field_mapping.get(key.lower(), key)
        normalized[normalized_key] = value
    
    # Ensure all required fields are present
    required_fields = ['name', 'calories', 'total_fat', 'carbohydrates', 'protein', 
                      'fiber', 'sugars', 'sodium', 'serving_size', 'health_analysis']
    
    for field in required_fields:
        if field not in normalized:
            normalized[field] = 0 if field in ['calories', 'total_fat', 'carbohydrates', 
                                             'protein', 'fiber', 'sugars', 'sodium'] else ''
    
    # Ensure health_analysis is properly structured
    if 'health_analysis' not in normalized:
        normalized['health_analysis'] = {
            'is_healthy': None,
            'message': 'Keep tracking your meals! Every meal logged is a step toward better health awareness.'
        }
    
    return normalized

@router.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

@router.get("/calorie_count/{query:path}")
async def calorie_count(query: str, user_id: str):
    try:
        # Get nutrition data and health analysis in one call
        meal_data = await get_meal_analysis(query)
        
        # Search for an image of the meal
        image_url = search_meal_image(meal_data["name"])
        if image_url:
            meal_data["image_url"] = image_url
        
        # Normalize the data
        meal_data = normalize_meal_data(meal_data)
        
        # Convert the response to the correct format if it contains multiple items
        if isinstance(meal_data.get('calories'), dict):
            # Sum up the values for each nutrient
            total_meal = {
                'name': query,
                'calories': sum(meal_data.get('calories', {}).values()),
                'total_fat': sum(meal_data.get('total_fat', {}).values()),
                'carbohydrates': sum(meal_data.get('carbohydrates', {}).values()),
                'protein': sum(meal_data.get('protein', {}).values()),
                'fiber': sum(meal_data.get('fiber', {}).values()),
                'sugars': sum(meal_data.get('sugars', {}).values()),
                'sodium': sum(meal_data.get('sodium', {}).values()),
                'serving_size': 'combined serving'
            }
            meal_data = normalize_meal_data(total_meal)
        
        # Store the transaction in the database
        await db_utils.add_transaction(user_id, meal_data)
        
        return meal_data
    except Exception as e:
        logger.error(f"Error processing meal info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_meal_analysis(query: str) -> dict:
    """Get nutrition data and health analysis using LLM in a single call"""
    try:
        # Create a combined prompt for both nutrition data and health analysis
        prompt = f"""Analyze the following meal: {query}

1. First, provide the nutritional values for each category:
{settings.nutrition}

2. Then, analyze if this meal is healthy or unhealthy based on its nutritional content.
If healthy, provide a unique encouraging message about making good choices.
If unhealthy, provide a gentle reminder about health but stay encouraging.

Return a single JSON object that includes both the nutritional data and health analysis, with these EXACT field names:
{{
    "name": "meal name",
    "calories": value,
    "total_fat": value,
    "carbohydrates": value,
    "protein": value,
    "fiber": value,
    "sugars": value,
    "sodium": value,
    "serving_size": "serving size",
    "health_analysis": {{
        "is_healthy": true or false,
        "message": "Your encouraging message here"
    }}
}}

Important: Use underscores in field names (total_fat, not total fat). Respond ONLY with the JSON object."""

        llm_response = await llm_service.send_to_llm(prompt)
        meal_data = await llm_service.format_response(llm_response)
        
        # Normalize the data
        meal_data = normalize_meal_data(meal_data)
        
        # Ensure health_analysis.is_healthy is boolean
        if isinstance(meal_data.get('health_analysis', {}).get('is_healthy'), str):
            meal_data['health_analysis']['is_healthy'] = meal_data['health_analysis']['is_healthy'].lower() == 'true'
        
        return meal_data
    except Exception as e:
        logger.error(f"Error analyzing meal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily_totals/")
async def get_daily_totals(user_id: str, target_date: Optional[str] = None):
    try:
        # Convert string date to date object if provided
        date_obj = None
        if target_date:
            try:
                date_obj = date.fromisoformat(target_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        totals = db_utils.get_daily_totals(user_id, date_obj)
        if totals is None:
            return {"message": "No data found for the specified date"}
        return totals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily_meals/")
async def get_daily_meals_endpoint(user_id: str, date: Optional[str] = None):
    try:
        if date:
            target_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        else:
            target_date = datetime.datetime.now().date()
        
        start_of_day = datetime.datetime.combine(target_date, datetime.time.min)
        end_of_day = datetime.datetime.combine(target_date, datetime.time.max)
        
        start_timestamp = int(start_of_day.timestamp())
        end_timestamp = int(end_of_day.timestamp())
        
        return await db_utils.get_daily_meals(user_id, start_timestamp, end_timestamp)
    except Exception as e:
        logger.error(f"Error getting daily meals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical_totals/")
async def get_historical_totals(user_id: str, days: int = 14):
    """Get historical daily totals for the last N days."""
    try:
        if days > 90:  # Limit to 90 days of history
            raise HTTPException(status_code=400, detail="Cannot request more than 90 days of history")
        
        totals = db_utils.get_historical_totals(user_id, days)
        return totals
    except Exception as e:
        logger.error(f"Error getting historical totals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/meal/{meal_id}")
async def delete_meal_endpoint(meal_id: int, user_id: str):
    try:
        await db_utils.delete_meal(meal_id, user_id)
        return {"message": "Meal deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/meal/{meal_text}")
async def get_meal_info(
    meal_text: str,
    user_id: Optional[str] = Query(None)
) -> dict:
    try:
        # Get nutrition data
        nutrition_data = await get_meal_analysis(meal_text)
        
        # Save to database if user_id provided
        if user_id:
            await db_utils.add_transaction(user_id, nutrition_data)
            
        return nutrition_data
    except Exception as e:
        logger.error(f"Error processing meal info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
