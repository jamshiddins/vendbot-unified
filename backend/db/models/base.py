"""Base database models"""
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func

# Создаем базовую модель без conflicting metadata
metadata = MetaData()
Base = declarative_base(metadata=metadata)

class TimestampMixin:
    """Mixin для добавления timestamp полей"""
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)