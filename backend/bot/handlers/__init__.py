from aiogram import Dispatcher
from . import start, admin, warehouse, operator

def setup_handlers(dp: Dispatcher):
    """Настройка всех обработчиков"""
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(warehouse.router)
    dp.include_router(operator.router)
