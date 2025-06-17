from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from db.database import get_db
from db.models.asset import AssetType
from api.schemas import AssetCreate, AssetUpdate, AssetResponse
from core.services.asset_service import AssetService

router = APIRouter()

@router.post("/", response_model=AssetResponse)
async def create_asset(
    asset_data: AssetCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создание нового актива (машина, бункер, гриндер)"""
    service = AssetService(db)
    return await service.create_asset(asset_data)

@router.get("/", response_model=List[AssetResponse])
async def get_assets(
    asset_type: Optional[AssetType] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Получение списка активов с фильтрацией по типу"""
    service = AssetService(db)
    return await service.get_assets(
        asset_type=asset_type,
        skip=skip,
        limit=limit
    )

@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение актива по ID"""
    service = AssetService(db)
    asset = await service.get_asset(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Актив не найден"
        )
    return asset

@router.get("/inventory/{inventory_number}", response_model=AssetResponse)
async def get_asset_by_inventory(
    inventory_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Получение актива по инвентарному номеру"""
    service = AssetService(db)
    asset = await service.get_asset_by_inventory(inventory_number)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Актив не найден"
        )
    return asset

@router.patch("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновление актива"""
    service = AssetService(db)
    asset = await service.update_asset(asset_id, asset_data)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Актив не найден"
        )
    return asset