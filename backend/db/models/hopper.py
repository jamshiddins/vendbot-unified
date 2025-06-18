"""Модель бункера для ингредиентов"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base

class HopperStatus(enum.Enum):
    EMPTY = "empty"
    FILLED = "filled"
    INSTALLED = "installed"
    CLEANING = "cleaning"
    RETURNED = "returned"

class Hopper(Base):
    __tablename__ = "hoppers"
    
    id = Column(Integer, primary_key=True)
    number = Column(String(20), unique=True, nullable=False)  # H001-H160
    
    # Физические параметры
    weight_empty = Column(Float)  # Вес пустого
    weight_with_lid = Column(Float)  # Вес с крышкой
    weight_full = Column(Float)  # Вес полного
    current_weight = Column(Float)  # Текущий вес
    
    # Состояние
    status = Column(Enum(HopperStatus), default=HopperStatus.EMPTY)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"))
    
    # Связи
    ingredient = relationship("Ingredient", back_populates="hoppers")
    machine_id = Column(Integer, ForeignKey("machines.id"))
    machine = relationship("Machine", back_populates="hoppers")
    operations = relationship("HopperOperation", back_populates="hopper")
    
    # Метаданные
    last_filled_date = Column(DateTime)
    last_cleaned_date = Column(DateTime)
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    assigned_to = relationship("User", back_populates="assigned_hoppers")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
