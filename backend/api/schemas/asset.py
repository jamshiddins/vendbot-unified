from pydantic import Field
from typing import Optional, Dict, Any
from db.models.asset import AssetType, AssetStatus
from .base import BaseSchema, TimestampSchema

class AssetBase(BaseSchema):
    type: AssetType
    inventory_number: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    serial_number: Optional[str] = None
    location: Optional[str] = None

class AssetCreate(AssetBase):
    status: AssetStatus = AssetStatus.ACTIVE
    metadata: Dict[str, Any] = {}

class AssetUpdate(BaseSchema):
    name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[AssetStatus] = None
    metadata: Optional[Dict[str, Any]] = None

class AssetResponse(AssetBase, TimestampSchema):
    id: int
    status: AssetStatus
    metadata: Dict[str, Any]