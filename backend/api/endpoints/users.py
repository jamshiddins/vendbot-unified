from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db.database import get_db
from api.schemas import UserCreate, UserUpdate, UserResponse
from core.services.user_service import UserService

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создание нового пользователя"""
    service = UserService(db)
    return await service.create_user(user_data)

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Получение списка пользователей"""
    service = UserService(db)
    return await service.get_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение пользователя по ID"""
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user

@router.get("/telegram/{telegram_id}", response_model=UserResponse)
async def get_user_by_telegram(
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение пользователя по Telegram ID"""
    service = UserService(db)
    user = await service.get_user_by_telegram(telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновление пользователя"""
    service = UserService(db)
    user = await service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user