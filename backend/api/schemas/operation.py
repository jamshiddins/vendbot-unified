from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import enum

# Определяем OperationType локально
class OperationType(str, enum.Enum):
    FILL = "fill"
    INSTALL = "install"
    REMOVE = "remove"
    CLEAN = "clean"
    CHECK = "check"

class HopperOperationBase(BaseModel):
    hopper_id: int
    operation_type: OperationType
    ingredient_id: Optional[int] = None
    quantity_added: Optional[float] = None
    machine_id: Optional[int] = None
    notes: Optional[str] = None

class HopperOperationCreate(HopperOperationBase):
    photos: Optional[List[str]] = []

class HopperOperationResponse(HopperOperationBase):
    id: int
    operator_id: int
    photos: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
