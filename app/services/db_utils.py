from app.core.config import settings
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models import Transaction, Base
from datetime import datetime, timezone, date, time, timedelta
from pathlib import Path
import json
import zoneinfo

# Use Central Time zone
CT_TIMEZONE = zoneinfo.ZoneInfo("America/Chicago")

DATABASE = f"db/{settings.database['name']}.sqlite3"
engine = create_engine(f'sqlite:///{DATABASE}')
Session = sessionmaker(bind=engine)

def create_tables():
    """Create database tables."""
    Path("db").mkdir(exist_ok=True)
    Base.metadata.create_all(engine)

def get_session():
    return Session()

async def add_transaction(user_uuid: str, food_data: dict):
    """Add a transaction to the database."""
    session = get_session()
    try:
        # Store timestamp as UTC but get current time from CT
        ct_now = datetime.now(CT_TIMEZONE)
        utc_timestamp = int(ct_now.astimezone(timezone.utc).timestamp())
        print(f"Adding transaction at CT time: {ct_now}, UTC timestamp: {utc_timestamp}")
        
        transaction = Transaction(
            user_id=user_uuid,
            timestamp=utc_timestamp,
            name=food_data['name'],
            calories=food_data['calories'],
            total_fat=food_data['total_fat'],  # Use normalized field name
            carbohydrates=food_data['carbohydrates'],
            protein=food_data['protein'],
            fiber=food_data['fiber'],
            sugars=food_data['sugars'],
            serving_size=food_data['serving_size'],  # Use normalized field name
            sodium=food_data['sodium']
        )
        
        session.add(transaction)
        session.commit()
        print(f"Successfully added transaction for {food_data['name']}")
    except Exception as e:
        print(f"Error adding transaction: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def get_daily_totals(user_uuid: str, target_date: date = None):
    session = get_session()
    try:
        if target_date is None:
            # Get current date in Central Time
            target_date = datetime.now(CT_TIMEZONE).date()
        
        # Convert date to datetime range for the full day in Central Time
        start_ct = datetime.combine(target_date, time.min).replace(tzinfo=CT_TIMEZONE)
        end_ct = datetime.combine(target_date, time.max).replace(tzinfo=CT_TIMEZONE)
        
        # Convert to UTC timestamps for database query
        start_utc = int(start_ct.astimezone(timezone.utc).timestamp())
        end_utc = int(end_ct.astimezone(timezone.utc).timestamp())
        
        print(f"Fetching totals for user {user_uuid}")
        print(f"CT Date range: {start_ct} to {end_ct}")
        print(f"UTC timestamps: {start_utc} to {end_utc}")
        
        # First, check if we have any transactions for this user
        total_count = session.query(func.count(Transaction.id)).filter(
            Transaction.user_id == user_uuid
        ).scalar()
        print(f"Total transactions for user: {total_count}")
        
        # Query for daily totals
        totals = session.query(
            func.sum(Transaction.calories).label('calories'),
            func.sum(Transaction.total_fat).label('total_fat'),
            func.sum(Transaction.carbohydrates).label('carbohydrates'),
            func.sum(Transaction.fiber).label('fiber'),
            func.sum(Transaction.sugars).label('sugars'),
            func.sum(Transaction.protein).label('protein'),
            func.sum(Transaction.sodium).label('sodium')
        ).filter(
            Transaction.user_id == user_uuid,
            Transaction.timestamp.between(start_utc, end_utc)
        ).first()
        
        print(f"Query results: {totals}")
        
        # Convert SQLAlchemy Row to dict
        result = {
            'calories': totals.calories or 0 if totals else 0,
            'total_fat': totals.total_fat or 0 if totals else 0,
            'carbohydrates': totals.carbohydrates or 0 if totals else 0,
            'protein': totals.protein or 0 if totals else 0,
            'fiber': totals.fiber or 0 if totals else 0,
            'sugars': totals.sugars or 0 if totals else 0,
            'sodium': totals.sodium or 0 if totals else 0
        }
        
        print(f"Returning daily totals: {result}")
        return result
    except Exception as e:
        print(f"Error getting daily totals: {e}")
        raise
    finally:
        session.close()

def get_historical_totals(user_uuid: str, days: int = 14):
    """Get daily totals for the last N days."""
    session = get_session()
    try:
        # Get current date in Central Time
        end_date = datetime.now(CT_TIMEZONE).date()
        start_date = end_date - timedelta(days=days-1)  # -1 because we want to include today
        
        daily_totals = []
        
        for single_date in (start_date + timedelta(n) for n in range(days)):
            # Get start and end of the day in Central Time
            start_ct = datetime.combine(single_date, time.min).replace(tzinfo=CT_TIMEZONE)
            end_ct = datetime.combine(single_date, time.max).replace(tzinfo=CT_TIMEZONE)
            
            # Convert to UTC timestamps for database query
            start_utc = int(start_ct.astimezone(timezone.utc).timestamp())
            end_utc = int(end_ct.astimezone(timezone.utc).timestamp())
            
            # Query for daily totals
            totals = session.query(
                func.sum(Transaction.calories).label('calories'),
                func.sum(Transaction.total_fat).label('total_fat'),
                func.sum(Transaction.carbohydrates).label('carbohydrates'),
                func.sum(Transaction.fiber).label('fiber'),
                func.sum(Transaction.sugars).label('sugars'),
                func.sum(Transaction.protein).label('protein'),
                func.sum(Transaction.sodium).label('sodium')
            ).filter(
                Transaction.user_id == user_uuid,
                Transaction.timestamp.between(start_utc, end_utc)
            ).first()
            
            # Convert SQLAlchemy Row to dict
            day_total = {
                'date': single_date.isoformat(),
                'calories': totals.calories or 0 if totals else 0,
                'total_fat': totals.total_fat or 0 if totals else 0,
                'carbohydrates': totals.carbohydrates or 0 if totals else 0,
                'protein': totals.protein or 0 if totals else 0,
                'fiber': totals.fiber or 0 if totals else 0,
                'sugars': totals.sugars or 0 if totals else 0,
                'sodium': totals.sodium or 0 if totals else 0
            }
            daily_totals.append(day_total)
        
        return daily_totals
    finally:
        session.close()

async def get_daily_meals(user_id: str, start_timestamp: int, end_timestamp: int) -> list:
    """Get all meals for a specific day."""
    session = get_session()
    try:
        # Add debug prints
        print(f"Fetching meals for user {user_id} between {start_timestamp} and {end_timestamp}")
        ct_start = datetime.fromtimestamp(start_timestamp, CT_TIMEZONE)
        ct_end = datetime.fromtimestamp(end_timestamp, CT_TIMEZONE)
        print(f"Central Time range: {ct_start} to {ct_end}")
        
        # First, check if the user exists and show all their meals
        count_row = session.query(func.count(Transaction.id)).filter(Transaction.user_id == user_id).scalar()
        total_meals = count_row
        print(f"Total meals in DB for user: {total_meals}")
        
        # Get all meals for debugging
        all_meals = session.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.timestamp.desc()).all()
        print(f"Found {len(all_meals)} total meals")
        
        # Now get meals for the specific time range
        meals = session.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.timestamp.between(start_timestamp, end_timestamp)
        ).order_by(Transaction.timestamp.desc()).all()
        
        result = []
        for meal in meals:
            # Convert UTC timestamp to Central Time for display
            ct_time = datetime.fromtimestamp(meal.timestamp, timezone.utc).astimezone(CT_TIMEZONE)
            meal_data = {
                'id': meal.id,  # Make sure ID is included
                'name': meal.name,
                'timestamp': int(ct_time.timestamp()),
                'calories': meal.calories,
                'total_fat': meal.total_fat,
                'carbohydrates': meal.carbohydrates,
                'protein': meal.protein,
                'fiber': meal.fiber,
                'sugars': meal.sugars,
                'serving_size': meal.serving_size,
                'sodium': meal.sodium
            }
            result.append(meal_data)
            print(f"Found meal in range: {meal_data}")
        
        print(f"Returning {len(result)} meals in the specified time range")
        return result
    except Exception as e:
        print(f"Error in get_daily_meals: {e}")
        raise e
    finally:
        session.close()

async def delete_meal(meal_id: int, user_id: str) -> bool:
    """Delete a meal from the database and return True if successful."""
    session = get_session()
    try:
        # Find the transaction and verify it belongs to the user
        transaction = session.query(Transaction).filter(
            Transaction.id == meal_id,
            Transaction.user_id == user_id
        ).first()
        
        if not transaction:
            return False
            
        session.delete(transaction)
        session.commit()
        print(f"Successfully deleted meal {meal_id} for user {user_id}")
        return True
    except Exception as e:
        print(f"Error deleting meal: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

# Create tables on module import
create_tables()