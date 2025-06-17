from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, func

Base = declarative_base()

class TimestampMixin:
    """Миксин для добавления временных меток"""
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)