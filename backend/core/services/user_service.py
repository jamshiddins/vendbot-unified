from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from db.models.user import User
from api.schemas import UserCreate, UserUpdate
from .base import BaseService

class UserService(BaseService[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Создание нового пользователя"""
        # Проверяем, существует ли пользователь с таким telegram_id
        existing = await self.get_user_by_telegram(user_data.telegram_id)
        if existing:
            raise ValueError("Пользователь с таким Telegram ID уже существует")
        
        return await self.create(**user_data.model_dump())
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        return await self.get(user_id)
    
    async def get_user_by_telegram(self, telegram_id: int) -> Optional[User]:
        """Получение пользователя по Telegram ID"""
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка пользователей"""
        return await self.get_multi(skip=skip, limit=limit)
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Обновление пользователя"""
        update_data = user_data.model_dump(exclude_unset=True)
        return await self.update(user_id, **update_data)
    
    async def get_active_users_by_role(self, role: str) -> List[User]:
        """Получение активных пользователей по роли"""
        result = await self.db.execute(
            select(User).where(
                User.role == role,
                User.is_active == True
            )
        )
        return result.scalars().all()