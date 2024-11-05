import sqlite3
from app.core.config import settings
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone
from pathlib import Path


DATABASE = f"db/{settings.database['name']}.sqlite3"

CREATE_USER_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_uuid TEXT UNIQUE NOT NULL,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    sex TEXT CHECK(sex IN ('male', 'female', 'other')) NOT NULL,
    age INTEGER NOT NULL,
    orig_weight REAL NOT NULL,
    target_weight REAL NOT NULL
    );
    """

CREATE_NUTRITION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS nutrition (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    transcript TEXT NOT NULL,
    result TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
"""

CREATE_TRANSACTION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    food_group TEXT,
    serving_size TEXT,
    calories INTEGER,  
    total_fat INTEGER,  
    saturated_fat INTEGER,  
    trans_fat INTEGER, 
    carbohydrates INTEGER,  
    fiber INTEGER, 
    sugars INTEGER,  
    protein INTEGER,  
    cholesterol INTEGER, 
    sodium INTEGER,      
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
"""

def create_tables():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(CREATE_USER_TABLE_SQL)
    cursor.execute(CREATE_TRANSACTION_TABLE_SQL)

    conn.commit()
    conn.close()

# Create an engine
engine = create_engine(f'sqlite:///{DATABASE}')
Base = declarative_base()

# Define your model
class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user.id'), nullable=False)
    name = Column(String, nullable=False)
    food_group = Column(String)
    serving_size = Column(String)
    calories = Column(Integer)
    total_fat = Column(Integer)
    saturated_fat = Column(Integer)
    trans_fat = Column(Integer)
    carbohydrates = Column(Integer)
    fiber = Column(Integer)
    sugars = Column(Integer)
    protein = Column(Integer)
    cholesterol = Column(Integer)
    sodium = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_uuid = Column(String, nullable=False, unique=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    sex = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    orig_weight = Column(Integer, nullable=False)
    target_weight = Column(Integer, nullable=False)


# Create a session
Session = sessionmaker(bind=engine)
session = Session()

new_user = User(
    user_uuid="user123",
    firstname="Steve",
    lastname='Kamer',
    sex='male',
    age=52,
    orig_weight=200,
    target_weight=180
    )

# Create a new transaction and add it to the session
new_transaction = Transaction(
    user_id="user123",
    name="Apple Pie",
    food_group="Dessert",
    serving_size="2 slices",
    calories=795,
    total_fat=44,
    saturated_fat=12,
    trans_fat=0,
    carbohydrates=185,
    fiber=4,
    sugars=19,
    protein=0,
    cholesterol=0,
    sodium=539
)

#session.add(new_user)
session.add(new_transaction)

# Commit the transaction
session.commit()

# Close the session
session.close()