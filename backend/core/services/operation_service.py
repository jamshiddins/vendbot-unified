from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime, timedelta
from db.models.operation import HopperOperation, OperationType
from db.models.asset import Asset, AssetType
from db.models.ingredient import Ingredient
from api.schemas import HopperOperationCreate
from .base import BaseService

class OperationService(BaseService[HopperOperation]):
    def __init__(self, db: AsyncSession):
        super().__init__(HopperOperation, db)
    
    async def create_hopper_operation(
        self, 
        operation_data: HopperOperationCreate,
        operator_id: int
    ) -> HopperOperation:
        """Создание операции с бункером"""
        # Проверяем существование бункера
        hopper = await self.db.get(Asset, operation_data.hopper_id)
        if not hopper or hopper.type != AssetType.HOPPER:
            raise ValueError("Бункер не найден")
        
        # Рассчитываем добавленное количество
        quantity_added = None
        if operation_data.quantity_before is not None and operation_data.quantity_after is not None:
            quantity_added = operation_data.quantity_after - operation_data.quantity_before
        
        # Создаем операцию
        operation = HopperOperation(
            hopper_id=operation_data.hopper_id,
            operation_type=operation_data.operation_type,
            ingredient_id=operation_data.ingredient_id,
            quantity_before=operation_data.quantity_before,
            quantity_after=operation_data.quantity_after,
            quantity_added=quantity_added,
            operator_id=operator_id,
            machine_id=operation_data.machine_id,
            photos=operation_data.photos,
            notes=operation_data.notes
        )
        
        self.db.add(operation)
        
        # Обновляем остатки ингредиента если это заполнение
        if operation_data.operation_type == OperationType.FILL and quantity_added:
            await self._update_ingredient_stock(
                operation_data.ingredient_id, 
                -quantity_added  # Уменьшаем склад
            )
        
        await self.db.commit()
        await self.db.refresh(operation)
        
        # Загружаем связанные объекты
        await self._load_relationships(operation)
        
        return operation
    
    async def _update_ingredient_stock(self, ingredient_id: int, delta: Decimal):
        """Обновление остатков ингредиента"""
        ingredient = await self.db.get(Ingredient, ingredient_id)
        if ingredient:
            ingredient.current_stock += delta
            if ingredient.current_stock < 0:
                ingredient.current_stock = 0
    
    async def _load_relationships(self, operation: HopperOperation):
        """Загрузка связанных объектов для ответа"""
        # Загружаем оператора
        await self.db.refresh(operation, ["operator", "hopper", "ingredient"])
    
    async def get_hopper_operations(
        self,
        hopper_id: Optional[int] = None,
        operator_id: Optional[int] = None,
        operation_type: Optional[OperationType] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[HopperOperation]:
        """Получение операций с фильтрацией"""
        query = select(HopperOperation)
        
        # Применяем фильтры
        conditions = []
        if hopper_id:
            conditions.append(HopperOperation.hopper_id == hopper_id)
        if operator_id:
            conditions.append(HopperOperation.operator_id == operator_id)
        if operation_type:
            conditions.append(HopperOperation.operation_type == operation_type)
        if date_from:
            conditions.append(HopperOperation.created_at >= date_from)
        if date_to:
            conditions.append(HopperOperation.created_at <= date_to)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(HopperOperation.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_consumption_analysis(
        self,
        machine_id: int,
        period_days: int = 7
    ) -> Dict:
        """Анализ расхода ингредиентов по машине"""
        date_from = datetime.utcnow() - timedelta(days=period_days)
        
        # Получаем операции заполнения для данной машины
        query = select(HopperOperation).where(
            and_(
                HopperOperation.machine_id == machine_id,
                HopperOperation.operation_type == OperationType.FILL,
                HopperOperation.created_at >= date_from,
                HopperOperation.quantity_added.isnot(None)
            )
        )
        
        result = await self.db.execute(query)
        operations = result.scalars().all()
        
        # Группируем по ингредиентам
        consumption = {}
        for op in operations:
            if op.ingredient_id:
                if op.ingredient_id not in consumption:
                    consumption[op.ingredient_id] = {
                        'total': Decimal('0'),
                        'operations_count': 0
                    }
                consumption[op.ingredient_id]['total'] += abs(op.quantity_added)
                consumption[op.ingredient_id]['operations_count'] += 1
        
        return {
            'period_days': period_days,
            'machine_id': machine_id,
            'consumption': consumption,
            'total_operations': len(operations)
        }