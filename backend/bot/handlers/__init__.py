from aiogram import Router

# Импортируем все роутеры
from .start import router as start_router
from .roles import router as roles_router
from .users import router as users_router  
from .machines import router as machines_router
from .hoppers import router as hoppers_router

# Главный роутер
router = Router()

# Подключаем все роутеры
router.include_router(start_router)
router.include_router(roles_router)  # Важно: roles идет перед users
router.include_router(users_router)
router.include_router(machines_router)
router.include_router(hoppers_router)

__all__ = ["router"]
