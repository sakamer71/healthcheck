from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)  # Unix timestamp
    name = Column(String, nullable=False)
    calories = Column(Float)
    total_fat = Column(Float)
    carbohydrates = Column(Float)
    protein = Column(Float)
    fiber = Column(Float)
    sugars = Column(Float)
    serving_size = Column(String)
    sodium = Column(Float)
