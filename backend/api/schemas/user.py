from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from db.models.user import UserRole
from .base import BaseSchema, TimestampSchema

class UserBase(BaseSchema):
    telegram_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    role: UserRole = UserRole.OPERATOR

class UserUpdate(BaseSchema):
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase, TimestampSchema):
    id: int
    role: UserRole
    is_active: bool