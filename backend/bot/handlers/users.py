from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db_session
from db.models import User
from bot.keyboards.inline import get_back_button
from bot.utils.permissions import check_permission

router = Router()

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Показать профиль пользователя"""
    async with get_db_session() as session:
        user = await session.get(User, message.from_user.id)
        
        if not user:
            await message.answer(" Профиль не найден. Используйте /start для регистрации.")
            return
        
        profile_text = f"""
 <b>Ваш профиль</b>

 ID: <code>{user.telegram_id}</code>
 Имя: {user.full_name}
 Телефон: {user.phone or 'Не указан'}
 Роль: {user.get_role_display()}
 Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}

 Команд выполнено: {user.commands_count or 0}
 Последняя активность: {user.last_activity.strftime('%d.%m.%Y %H:%M') if user.last_activity else 'Нет данных'}
"""
        
        await message.answer(profile_text, parse_mode="HTML")

@router.callback_query(F.data == "profile")
async def callback_profile(callback: CallbackQuery):
    """Показать профиль через callback"""
    await cmd_profile(callback.message)
    await callback.answer()

@router.message(Command("users"))
async def cmd_users_list(message: Message):
    """Список пользователей (только для админов)"""
    if not await check_permission(message.from_user.id, "admin"):
        await message.answer(" У вас нет прав для просмотра списка пользователей.")
        return
    
    async with get_db_session() as session:
        # Здесь будет логика получения списка пользователей
        await message.answer(" Функция списка пользователей в разработке...")
