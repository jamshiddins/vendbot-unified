from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from bot.keyboards.inline import get_main_menu

router = Router(name="common")

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Команда помощи"""
    help_text = """
<b> Справка по боту VendBot</b>

<b>Основные команды:</b>
/start - Начало работы
/menu - Главное меню
/help - Эта справка
/profile - Ваш профиль

<b>По вопросам обращайтесь:</b>
@vendbot_support
"""
    await message.answer(help_text)

@router.message(Command("menu"))
async def cmd_menu(message: Message, session):
    """Главное меню"""
    from db.models import User
    from sqlalchemy import select
    
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    await message.answer(
        "<b> Главное меню</b>\n\nВыберите действие:",
        reply_markup=get_main_menu(user)
    )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, session):
    """Возврат в главное меню"""
    from db.models import User
    from sqlalchemy import select
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    await callback.message.edit_text(
        "<b> Главное меню</b>\n\nВыберите действие:",
        reply_markup=get_main_menu(user)
    )
    await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery):
    """Отмена действия"""
    await callback.message.delete()
    await callback.answer("Действие отменено")

@router.callback_query(F.data == "about")
async def about_bot(callback: CallbackQuery):
    """О боте"""
    about_text = """
<b>ℹ О системе VendBot</b>

VendBot - современная система управления вендинговыми автоматами.

<b>Версия:</b> 2.0.0
<b>Разработчик:</b> VendBot Team

<b>Возможности:</b>
- Управление автоматами
- Складской учет
- Маршрутизация
- Аналитика и отчеты
"""
    await callback.message.answer(about_text)
    await callback.answer()
