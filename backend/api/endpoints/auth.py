from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from pydantic import BaseModel
from db.database import get_db
from core.services.user_service import UserService
from core.auth import AuthService
from core.config import settings

router = APIRouter()

class LoginRequest(BaseModel):
    telegram_id: int
    username: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Вход через Telegram ID"""
    user_service = UserService(db)
    
    # Проверяем существующего пользователя
    user = await user_service.get_user_by_telegram(login_data.telegram_id)
    
    if not user:
        # Создаем нового пользователя
        from api.schemas import UserCreate
        user_data = UserCreate(
            telegram_id=login_data.telegram_id,
            username=login_data.username
        )
        user = await user_service.create_user(user_data)
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Создаем токен
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role.value
        }
    )

@router.get("/me")
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    return {
        "id": current_user.id,
        "telegram_id": current_user.telegram_id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "is_active": current_user.is_active
    }