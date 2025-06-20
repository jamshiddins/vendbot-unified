from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from db.models import User
from bot.keyboards.inline import get_main_menu
from core.config import settings

router = Router()
logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, bot):
    '''Обработчик команды /start'''
    
    # Проверяем есть ли пользователь в БД
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Создаем нового пользователя
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name or 'Без имени',
            is_active=False  # По умолчанию неактивен!
        )
        
        # Владелец всегда активен
        if message.from_user.id == 42283329:
            user.is_active = True
            user.roles = ['admin']
        
        session.add(user)
        await session.commit()
        
        # Уведомляем владельца о новом пользователе
        if message.from_user.id != 42283329:
            try:
                await bot.send_message(
                    42283329,
                    f' <b>Новый пользователь!</b>\n\n'
                    f' Имя: {user.full_name}\n'
                    f' ID: {user.telegram_id}\n'
                    f' Username: @{user.username or "нет"}\n\n'
                    f'Используйте /role для активации',
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                        InlineKeyboardButton(
                            text=" Управление ролями",
                            callback_data="cmd_role"
                        )
                    ]])
                )
            except:
                pass
    
    # Проверяем активность
    if not user.is_active and user.telegram_id != 42283329:
        await message.answer(
            ' <b>Доступ ограничен</b>\n\n'
            'Ваш аккаунт ожидает активации.\n'
            'Администратор получил уведомление о вашей регистрации.\n\n'
            'Пожалуйста, подождите подтверждения.'
        )
        return
    
    # Для активных пользователей показываем меню
    welcome_text = (
        f' <b>Добро пожаловать, {user.full_name}!</b>\n\n'
        f' Я - VendBot, система управления вендинговыми автоматами.\n'
    )
    
    if user.roles:
        welcome_text += f'\n <b>Ваши роли:</b> {user.role_display}\n'
    
    welcome_text += '\nВыберите действие из меню:'
    
    await message.answer(welcome_text, reply_markup=get_main_menu(user))
