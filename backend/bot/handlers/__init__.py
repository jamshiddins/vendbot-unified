from aiogram import Dispatcher
from .start import router as start_router
from .admin import router as admin_router
from .warehouse import router as warehouse_router
from .operator import router as operator_router

def setup_handlers(dp: Dispatcher):
    """Настройка всех обработчиков"""
    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(warehouse_router) 
    dp.include_router(operator_router)