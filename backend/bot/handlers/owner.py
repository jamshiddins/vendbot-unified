from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import logging

from db.models import User, UserRole
from bot.keyboards.inline import get_users_list_keyboard, get_role_selection_keyboard
from core.config import settings

router = Router()
logger = logging.getLogger(__name__)

# ID владельца системы
OWNER_ID = 42283329

@router.message(Command("role"))
async def cmd_role(message: Message, session: AsyncSession):
    '''Команда управления ролями - только для владельца'''
    
    # Проверяем что это владелец
    if message.from_user.id != OWNER_ID:
        # Для всех остальных команда не существует
        return
    
    # Получаем список всех пользователей
    result = await session.execute(
        select(User).order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    
    if not users:
        await message.answer(
            ' <b>Нет зарегистрированных пользователей</b>\n\n'
            'Пользователи появятся после использования команды /start'
        )
        return
    
    await message.answer(
        ' <b>Управление ролями пользователей</b>\n\n'
        'Выберите пользователя для изменения роли:',
        reply_markup=get_users_list_keyboard(users)
    )

@router.callback_query(F.data.startswith('user_role:'))
async def select_user_for_role(callback: CallbackQuery, session: AsyncSession):
    '''Выбор пользователя для изменения роли'''
    
    # Проверяем что это владелец
    if callback.from_user.id != OWNER_ID:
        await callback.answer(' Нет доступа', show_alert=True)
        return
    
    user_id = int(callback.data.split(':')[1])
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer(' Пользователь не найден', show_alert=True)
        return
    
    # Показываем выбор ролей
    text = (
        f' <b>Пользователь:</b> {user.full_name}\n'
        f' <b>ID:</b> {user.telegram_id}\n'
        f' <b>Username:</b> @{user.username or "нет"}\n'
        f' <b>Текущие роли:</b> {", ".join(user.roles) if user.roles else "нет"}\n'
        f' <b>Статус:</b> {" Активен" if user.is_active else " Неактивен"}\n\n'
        'Выберите действие:'
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_role_selection_keyboard(user.telegram_id, user.roles or [])
    )

@router.callback_query(F.data.startswith('toggle_role:'))
async def toggle_user_role(callback: CallbackQuery, session: AsyncSession):
    '''Переключение роли пользователя'''
    
    # Проверяем что это владелец
    if callback.from_user.id != OWNER_ID:
        await callback.answer(' Нет доступа', show_alert=True)
        return
    
    _, user_id, role = callback.data.split(':')
    user_id = int(user_id)
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer(' Пользователь не найден', show_alert=True)
        return
    
    # Изменяем роли
    roles = set(user.roles or [])
    if role in roles:
        roles.remove(role)
        action = 'удалена'
    else:
        roles.add(role)
        action = 'добавлена'
    
    user.roles = list(roles)
    await session.commit()
    
    await callback.answer(f' Роль {role} {action}')
    
    # Обновляем сообщение
    text = (
        f' <b>Пользователь:</b> {user.full_name}\n'
        f' <b>ID:</b> {user.telegram_id}\n'
        f' <b>Username:</b> @{user.username or "нет"}\n'
        f' <b>Текущие роли:</b> {", ".join(user.roles) if user.roles else "нет"}\n'
        f' <b>Статус:</b> {" Активен" if user.is_active else " Неактивен"}\n\n'
        'Выберите действие:'
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_role_selection_keyboard(user.telegram_id, user.roles or [])
    )

@router.callback_query(F.data.startswith('toggle_active:'))
async def toggle_user_active(callback: CallbackQuery, session: AsyncSession):
    '''Активация/деактивация пользователя'''
    
    # Проверяем что это владелец
    if callback.from_user.id != OWNER_ID:
        await callback.answer(' Нет доступа', show_alert=True)
        return
    
    user_id = int(callback.data.split(':')[1])
    
    # Нельзя деактивировать себя
    if user_id == OWNER_ID:
        await callback.answer(' Нельзя деактивировать владельца', show_alert=True)
        return
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer(' Пользователь не найден', show_alert=True)
        return
    
    # Переключаем статус
    user.is_active = not user.is_active
    await session.commit()
    
    await callback.answer(
        f' Пользователь {"активирован" if user.is_active else "деактивирован"}'
    )
    
    # Обновляем сообщение
    text = (
        f' <b>Пользователь:</b> {user.full_name}\n'
        f' <b>ID:</b> {user.telegram_id}\n'
        f' <b>Username:</b> @{user.username or "нет"}\n'
        f' <b>Текущие роли:</b> {", ".join(user.roles) if user.roles else "нет"}\n'
        f' <b>Статус:</b> {" Активен" if user.is_active else " Неактивен"}\n\n'
        'Выберите действие:'
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_role_selection_keyboard(user.telegram_id, user.roles or [])
    )
