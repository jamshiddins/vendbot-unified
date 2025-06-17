from fastapi import APIRouter
from api.endpoints import users, assets, ingredients, operations

api_router = APIRouter()

# Подключаем все роуты
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(ingredients.router, prefix="/ingredients", tags=["ingredients"])
api_router.include_router(operations.router, prefix="/operations", tags=["operations"])