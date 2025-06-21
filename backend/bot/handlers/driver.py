from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

router = Router()

@router.message(Command("driver"))
async def cmd_driver_menu(message: Message):
    """Меню водителя"""
    await message.answer("🚛 Меню водителя в разработке...")

@router.callback_query(F.data == "driver_menu")
async def callback_driver_menu(callback: CallbackQuery):
    """Callback меню водителя"""
    await callback.message.answer(" Функции водителя будут доступны в следующей версии")
    await callback.answer()
