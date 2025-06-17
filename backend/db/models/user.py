from sqlalchemy import Column, Integer, String, BigInteger, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
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
    
    # Relationships
    operations = relationship("HopperOperation", back_populates="operator")
    
    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"