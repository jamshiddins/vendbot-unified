"""Модель операций с бункерами"""
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base

class OperationType(enum.Enum):
    FILL = "fill"
    INSTALL = "install"
    REMOVE = "remove"
    CLEAN = "clean"
    WEIGH = "weigh"
    TRANSFER = "transfer"
    RETURN = "return"

class HopperOperation(Base):
    __tablename__ = "hopper_operations"  # Временно новое имя
    
    id = Column(Integer, primary_key=True)
    operation_type = Column(Enum(OperationType), nullable=False)
    
    # Связи
    hopper_id = Column(Integer, ForeignKey("hoppers.id"), nullable=False)
    hopper = relationship("Hopper", back_populates="operations")
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="hopper_operations")
    
    machine_id = Column(Integer, ForeignKey("machines.id"))
    machine = relationship("Machine", back_populates="hopper_operations")
    
    # Данные операции
    weight_before = Column(Float)
    weight_after = Column(Float)
    photo_before_url = Column(Text)
    photo_after_url = Column(Text)
    notes = Column(Text)
    
    # Метаданные
    performed_at = Column(DateTime, default=datetime.utcnow)
    location_lat = Column(Float)
    location_lon = Column(Float)

