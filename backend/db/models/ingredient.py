from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Ingredient(Base, TimestampMixin):
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    unit = Column(String(20), default="kg")
    current_stock = Column(Numeric(10, 3), default=0)
    min_stock = Column(Numeric(10, 3), default=0)
    cost = Column(Numeric(10, 2), default=0)
    category = Column(String(50))
    
    # Relationships
    hoppers = relationship("Hopper", back_populates="ingredient")
    
    def __repr__(self):
        return f"<Ingredient {self.code} - {self.name}>"

