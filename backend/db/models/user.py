from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    WAREHOUSE = "warehouse"
    OPERATOR = "operator"
    DRIVER = "driver"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь с ролями
    roles = relationship("UserRoleAssignment", back_populates="user", cascade="all, delete-orphan")
    
    def has_role(self, role: UserRole) -> bool:
        """Проверка наличия роли"""
        return any(r.role == role and r.is_active for r in self.roles)
    
    def get_roles(self):
        """Получить список активных ролей"""
        return [r.role for r in self.roles if r.is_active]

class UserRoleAssignment(Base):
    __tablename__ = "user_role_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    assigned_by = Column(Integer, nullable=False)  # telegram_id того, кто назначил
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Уникальное ограничение на пару user_id + role
    __table_args__ = (UniqueConstraint('user_id', 'role', name='_user_role_uc'),)
    
    # Связи
    user = relationship("User", back_populates="roles")
