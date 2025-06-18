from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from db.models import Ingredient
from bot.keyboards.inline import get_back_button

router = Router()

@router.callback_query(F.data.in_(["warehouse_stock", "warehouse_receive", "warehouse_assign", "warehouse_returns"]))
async def redirect_to_hoppers(callback: CallbackQuery, session: AsyncSession):
    """Перенаправить на управление бункерами"""
    from .hopper_management import show_hopper_menu
    await show_hopper_menu(callback, session)
async def show_stock(callback: CallbackQuery, session: AsyncSession):
    """Показать остатки на складе"""
    
    # Получаем все ингредиенты
    result = await session.execute(select(Ingredient).order_by(Ingredient.name))
    ingredients: List[Ingredient] = result.scalars().all()
    
    text = " <b>Остатки на складе:</b>\n\n"
    
    if not ingredients:
        text += "Склад пуст"
    else:
        for ing in ingredients:
            stock_emoji = "" if ing.current_stock > 10 else "" if ing.current_stock > 0 else ""
            text += (
                f"{stock_emoji} <b>{ing.name}</b>\n"
                f"   Код: {ing.code}\n"
                f"   Остаток: {ing.current_stock} {ing.unit}\n\n"
            )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "warehouse_receive")
async def receive_goods(callback: CallbackQuery, session: AsyncSession):
    """Поступление товара"""
    await callback.message.edit_text(
        " <b>Поступление товара</b>\n\n"
        "Функция в разработке...",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "warehouse_assign")
async def assign_goods(callback: CallbackQuery, session: AsyncSession):
    """Назначить товар"""
    await callback.message.edit_text(
        " <b>Назначение товара</b>\n\n"
        "Функция в разработке...",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "warehouse_returns")
async def show_returns(callback: CallbackQuery, session: AsyncSession):
    """Возвраты"""
    await callback.message.edit_text(
        " <b>Возвраты</b>\n\n"
        "Функция в разработке...",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()

__all__ = ["router"]

