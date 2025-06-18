from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class IngredientBase(BaseModel):
    name: str
    code: str
    unit: str = "kg"
    min_stock: float = 0.0
    current_stock: float = 0.0
    category: Optional[str] = None

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    unit: Optional[str] = None
    min_stock: Optional[float] = None
    current_stock: Optional[float] = None
    category: Optional[str] = None

class IngredientResponse(IngredientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
