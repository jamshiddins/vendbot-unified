from sqlalchemy import Column, Integer, String, BigInteger, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .base import Base, TimestampMixin

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    WAREHOUSE = "warehouse"
    OPERATOR = "operator"
    DRIVER = "driver"

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String(100))
    full_name = Column(String(200))
    role = Column(Enum(UserRole), default=UserRole.OPERATOR)
    is_active = Column(Boolean, default=True)
    phone = Column(String(20))
    
    # Relationships для вендинга
    machines = relationship("Machine", back_populates="operator", foreign_keys="Machine.operator_id")
    assigned_hoppers = relationship("Hopper", back_populates="assigned_to", foreign_keys="Hopper.assigned_to_id")
    hopper_operations = relationship("HopperOperation", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"
