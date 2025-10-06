from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)  # UTC timestamp
    name = Column(String, nullable=False)
    calories = Column(Float, nullable=False)
    total_fat = Column(Float, nullable=False)
    carbohydrates = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    fiber = Column(Float, nullable=False)
    sugars = Column(Float, nullable=False)
    sodium = Column(Float, nullable=False)
    serving_size = Column(String, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp,
            'name': self.name,
            'calories': self.calories,
            'total_fat': self.total_fat,
            'carbohydrates': self.carbohydrates,
            'protein': self.protein,
            'fiber': self.fiber,
            'sugars': self.sugars,
            'sodium': self.sodium,
            'serving_size': self.serving_size
        }
