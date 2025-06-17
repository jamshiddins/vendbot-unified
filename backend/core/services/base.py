from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy import select
from db.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseService(Generic[ModelType]):
    """Базовый сервис с CRUD операциями"""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get(self, id: int) -> Optional[ModelType]:
        """Получить запись по ID"""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """Получить несколько записей"""
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, **kwargs) -> ModelType:
        """Создать новую запись"""
        db_obj = self.model(**kwargs)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Обновить запись"""
        db_obj = await self.get(id)
        if not db_obj:
            return None
        
        for field, value in kwargs.items():
            if value is not None:
                setattr(db_obj, field, value)
        
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: int) -> bool:
        """Удалить запись"""
        db_obj = await self.get(id)
        if not db_obj:
            return False
        
        await self.db.delete(db_obj)
        await self.db.commit()
        return True