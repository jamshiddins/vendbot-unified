from sqlalchemy import Column, Integer, BigInteger, String, Boolean, JSON, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from db.database import Base

class UserRole(str, enum.Enum):
    ADMIN = 'admin'
    WAREHOUSE = 'warehouse' 
    OPERATOR = 'operator'
    DRIVER = 'driver'

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(100))
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20))
    
    # Роли хранятся как JSON массив строк
    roles = Column(JSON, default=list)  # ['admin', 'warehouse'] etc
    
    # Статус активности
    is_active = Column(Boolean, default=False)  # По умолчанию неактивен
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Отношения
    hopper_operations = relationship('HopperOperation', back_populates='user')
    
    def has_role(self, role: str) -> bool:
        '''Проверка наличия роли'''
        return role in (self.roles or [])
    
    def has_any_role(self, *roles) -> bool:
        '''Проверка наличия хотя бы одной из ролей'''
        user_roles = set(self.roles or [])
        return bool(user_roles.intersection(roles))
    
    def add_role(self, role: str):
        '''Добавление роли'''
        if not self.roles:
            self.roles = []
        if role not in self.roles:
            self.roles.append(role)
    
    def remove_role(self, role: str):
        '''Удаление роли'''
        if self.roles and role in self.roles:
            self.roles.remove(role)
    
    @property
    def is_owner(self) -> bool:
        '''Проверка является ли пользователь владельцем'''
        return self.telegram_id == 42283329
    
    @property
    def role_display(self) -> str:
        '''Отображение ролей'''
        if not self.roles:
            return 'Нет ролей'
        
        role_names = {
            'admin': ' Администратор',
            'warehouse': ' Склад',
            'operator': ' Оператор',
            'driver': ' Водитель'
        }
        
        return ', '.join(role_names.get(r, r) for r in self.roles)
