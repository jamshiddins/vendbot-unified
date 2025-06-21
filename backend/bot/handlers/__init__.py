from aiogram import Router

from .start import router as start_router
from .admin import router as admin_router
from .warehouse import router as warehouse_router
from .operator import router as operator_router
from .hopper_management import router as hopper_router
from .admin_machines import router as admin_machines_router
from .owner import router as owner_router
from .roles import router as roles_router
from .users import router as users_router  # Добавляем импорт

def setup_handlers(dp):
    """Регистрация всех хендлеров"""
    dp.include_router(start_router)
    dp.include_router(users_router)  # Добавляем регистрацию
    dp.include_router(admin_router)
    dp.include_router(warehouse_router)
    dp.include_router(operator_router)
    dp.include_router(hopper_router)
    dp.include_router(admin_machines_router)
    dp.include_router(owner_router)
    dp.include_router(roles_router)
