﻿from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from db.models.base import Base, TimestampMixin
import enum

class AssetType(str, enum.Enum):
    MACHINE = "machine"
    HOPPER = "hopper"

class AssetStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"

class Asset(Base, TimestampMixin):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    asset_type = Column(Enum(AssetType), nullable=False)
    serial_number = Column(String(50), unique=True)
    location = Column(String(200))
    status = Column(Enum(AssetStatus), default=AssetStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    
    # Relationships будут добавлены позже
