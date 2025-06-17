from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from typing import Union
from db.database import AsyncSessionLocal
from core.services.user_service import UserService
from db.models.user import UserRole

class RoleFilter(BaseFilter):
    """Фильтр для проверки роли пользователя"""
    
    def __init__(self, role: Union[UserRole, list[UserRole]]):
        self.allowed_roles = [role] if isinstance(role, UserRole) else role
    
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        user_id = event.from_user.id
        
        async with AsyncSessionLocal() as db:
            service = UserService(db)
            user = await service.get_user_by_telegram(user_id)
            
            if not user or not user.is_active:
                return False
            
            return user.role in self.allowed_roles