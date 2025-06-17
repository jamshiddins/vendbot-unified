from pydantic import Field, validator
from typing import Optional, List, Dict
from decimal import Decimal
from db.models.operation import OperationType
from .base import BaseSchema, TimestampSchema

class HopperOperationCreate(BaseSchema):
    hopper_id: int
    operation_type: OperationType
    ingredient_id: Optional[int] = None
    quantity_before: Optional[Decimal] = Field(None, ge=0, decimal_places=3)
    quantity_after: Optional[Decimal] = Field(None, ge=0, decimal_places=3)
    machine_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=500)
    photos: List[str] = []
    
    @validator('quantity_after')
    def validate_quantities(cls, v, values):
        if v is not None and 'quantity_before' in values:
            if values['quantity_before'] is not None and v < 0:
                raise ValueError('Количество не может быть отрицательным')
        return v

class HopperOperationResponse(BaseSchema, TimestampSchema):
    id: int
    hopper_id: int
    operation_type: OperationType
    ingredient_id: Optional[int]
    quantity_before: Optional[Decimal]
    quantity_after: Optional[Decimal]
    quantity_added: Optional[Decimal]
    operator_id: int
    machine_id: Optional[int]
    photos: List[str]
    notes: Optional[str]
    sync_status: Dict[str, bool]
    
    # Вложенные объекты
    operator: Optional[dict] = None
    hopper: Optional[dict] = None
    ingredient: Optional[dict] = None