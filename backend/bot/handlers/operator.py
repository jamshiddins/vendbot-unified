from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from bot.keyboards.inline import get_back_button

router = Router()

# Перенаправляем все операции с бункерами на hopper_management
@router.callback_query(F.data.in_(["operator_tasks", "operator_machines", "operator_install", "operator_remove"]))
async def redirect_to_hoppers(callback: CallbackQuery):
    """Перенаправить на управление бункерами"""
    from .hopper_management import show_hopper_menu
    await show_hopper_menu(callback, callback.data['session'])

__all__ = ["router"]
