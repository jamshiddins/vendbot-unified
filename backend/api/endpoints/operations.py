from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from db.database import get_db
from db.models.operation import OperationType
from api.schemas import HopperOperationCreate, HopperOperationResponse
from core.services.operation_service import OperationService

router = APIRouter()

@router.post("/hopper", response_model=HopperOperationResponse)
async def create_hopper_operation(
    operation_data: HopperOperationCreate,
    operator_id: int = Query(..., description="ID оператора"),
    db: AsyncSession = Depends(get_db)
):
    """Создание операции с бункером"""
    service = OperationService(db)
    try:
        return await service.create_hopper_operation(operation_data, operator_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/hopper", response_model=List[HopperOperationResponse])
async def get_hopper_operations(
    hopper_id: Optional[int] = None,
    operator_id: Optional[int] = None,
    operation_type: Optional[OperationType] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Получение операций с бункерами"""
    service = OperationService(db)
    return await service.get_hopper_operations(
        hopper_id=hopper_id,
        operator_id=operator_id,
        operation_type=operation_type,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit
    )

@router.get("/hopper/{operation_id}", response_model=HopperOperationResponse)
async def get_hopper_operation(
    operation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение операции по ID"""
    service = OperationService(db)
    operation = await service.get(operation_id)
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Операция не найдена"
        )
    return operation

@router.get("/consumption/{machine_id}")
async def get_consumption_analysis(
    machine_id: int,
    period_days: int = Query(7, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Анализ расхода ингредиентов по машине"""
    service = OperationService(db)
    return await service.get_consumption_analysis(machine_id, period_days)