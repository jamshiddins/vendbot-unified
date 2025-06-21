from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

router = Router()

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Команда помощи"""
    help_text = """
 <b>Помощь по командам VendBot</b>

 /start - Начать работу с ботом
 /help - Показать это сообщение
 /profile - Ваш профиль
 /cancel - Отменить текущую операцию

<i>Выберите вашу роль через /start для доступа к специальным функциям</i>
"""
    await message.answer(help_text)

@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    """Callback помощи"""
    await cmd_help(callback.message)
    await callback.answer()

@router.message(Command("cancel"))
async def cmd_cancel(message: Message):
    """Отмена операции"""
    await message.answer(" Операция отменена", reply_markup=None)
