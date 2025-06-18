"""Модель кофейного автомата"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Machine(Base):
    __tablename__ = "machines"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)  # CVM-001
    name = Column(String(200), nullable=False)
    location = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String(50), default="active")  # active, maintenance, inactive
    
    # Связи
    operator_id = Column(Integer, ForeignKey("users.id"))
    operator = relationship("User", back_populates="machines")
    hoppers = relationship("Hopper", back_populates="machine")
    hopper_operations = relationship("HopperOperation", back_populates="machine")
    
    # Метаданные
    installation_date = Column(DateTime)
    last_service_date = Column(DateTime)
    next_service_date = Column(DateTime)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
