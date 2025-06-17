from aiogram import Router
from .hopper_fill import router as fill_router
from .hopper_install import router as install_router
from .hopper_remove import router as remove_router

router = Router(name="operator")

# Подключаем все роутеры оператора
router.include_router(fill_router)
router.include_router(install_router)
router.include_router(remove_router)