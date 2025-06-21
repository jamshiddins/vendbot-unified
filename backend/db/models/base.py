from enum import Enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Float, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TimestampMixin:
    """Mixin for adding created_at and updated_at timestamps"""
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class UserRole(str, Enum):
    """User roles in the system"""
    ADMIN = "admin"
    WAREHOUSE = "warehouse"
    OPERATOR = "operator"
    DRIVER = "driver"

# Association table for many-to-many relationship
user_roles_table = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', BigInteger, ForeignKey('users.telegram_id'), primary_key=True),
    Column('role', String(50), primary_key=True)
)

class User(Base, TimestampMixin):
    """User model"""
    __tablename__ = "users"
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    roles: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    @property
    def role_display(self) -> str:
        """Display user roles"""
        if not self.roles:
            return "Без роли"
        return ", ".join(self.roles)

class MachineStatus(str, Enum):
    """Machine statuses"""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"

class Machine(Base, TimestampMixin):
    """Coffee machine model"""
    __tablename__ = "machines"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[MachineStatus] = mapped_column(String(20), default=MachineStatus.ACTIVE)

class HopperStatus(str, Enum):
    """Hopper statuses"""
    EMPTY = "empty"
    FILLED = "filled"
    INSTALLED = "installed"
    CLEANING = "cleaning"

class Hopper(Base, TimestampMixin):
    """Hopper model"""
    __tablename__ = "hoppers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    status: Mapped[HopperStatus] = mapped_column(String(20), default=HopperStatus.EMPTY)
    machine_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('machines.id'), nullable=True)
    assigned_operator_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey('users.telegram_id'), nullable=True)

class Ingredient(Base, TimestampMixin):
    """Ingredient model"""
    __tablename__ = "ingredients"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="kg")

# Export all models
__all__ = [
    'Base',
    'TimestampMixin',
    'User',
    'UserRole',
    'user_roles_table',
    'Machine',
    'MachineStatus',
    'Hopper',
    'HopperStatus',
    'Ingredient'
]
