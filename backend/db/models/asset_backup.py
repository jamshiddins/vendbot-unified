"""Asset model"""
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum

class AssetType(enum.Enum):
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
    serial_number = Column(String(50), unique=True, nullable=True)
    location = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # НЕ добавляйте поле metadata - оно зарезервировано!