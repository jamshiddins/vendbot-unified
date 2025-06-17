from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from db.models.asset import Asset, AssetType, AssetStatus
from api.schemas import AssetCreate, AssetUpdate
from .base import BaseService
import random
import string

class AssetService(BaseService[Asset]):
    def __init__(self, db: AsyncSession):
        super().__init__(Asset, db)
    
    async def create_asset(self, asset_data: AssetCreate) -> Asset:
        """Создание нового актива"""
        # Генерируем инвентарный номер если не указан
        if not asset_data.inventory_number:
            asset_data.inventory_number = await self._generate_inventory_number(
                asset_data.type
            )
        
        # Проверяем уникальность инвентарного номера
        existing = await self.get_asset_by_inventory(asset_data.inventory_number)
        if existing:
            raise ValueError("Актив с таким инвентарным номером уже существует")
        
        return await self.create(**asset_data.model_dump())
    
    async def _generate_inventory_number(self, asset_type: AssetType) -> str:
        """Генерация инвентарного номера"""
        prefix = {
            AssetType.MACHINE: "MCH",
            AssetType.HOPPER: "HOP",
            AssetType.GRINDER: "GRN"
        }.get(asset_type, "AST")
        
        # Генерируем уникальный суффикс
        while True:
            suffix = ''.join(random.choices(string.digits, k=6))
            inv_number = f"{prefix}-{suffix}"
            
            # Проверяем уникальность
            existing = await self.get_asset_by_inventory(inv_number)
            if not existing:
                return inv_number
    
    async def get_asset_by_inventory(self, inventory_number: str) -> Optional[Asset]:
        """Получение актива по инвентарному номеру"""
        result = await self.db.execute(
            select(Asset).where(Asset.inventory_number == inventory_number)
        )
        return result.scalar_one_or_none()
    
    async def get_assets(
        self,
        asset_type: Optional[AssetType] = None,
        status: Optional[AssetStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """Получение активов с фильтрацией"""
        query = select(Asset)
        
        if asset_type:
            query = query.where(Asset.type == asset_type)
        if status:
            query = query.where(Asset.status == status)
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_available_hoppers(self) -> List[Asset]:
        """Получение доступных бункеров"""
        result = await self.db.execute(
            select(Asset).where(
                Asset.type == AssetType.HOPPER,
                Asset.status == AssetStatus.ACTIVE
            )
        )
        return result.scalars().all()
    
    async def update_asset(self, asset_id: int, asset_data: AssetUpdate) -> Optional[Asset]:
        """Обновление актива"""
        update_data = asset_data.model_dump(exclude_unset=True)
        return await self.update(asset_id, **update_data)