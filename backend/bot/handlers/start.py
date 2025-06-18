from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from db.models import User, UserRole
from bot.keyboards.inline import get_main_menu

router = Router()
logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    """Обработчик команды /start"""
    
    # Логируем информацию о пользователе
    logger.info(f"Start command from user: ID={message.from_user.id}, username=@{message.from_user.username}, name={message.from_user.full_name}")
    
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
            full_name=message.from_user.full_name,
            role=UserRole.OPERATOR,
            is_active=False
        )
        session.add(user)
        await session.commit()

        await message.answer(
            f" Добро пожаловать в VendBot!\n\n"
            f"Ваш аккаунт создан, но требует активации администратором.\n"
            f"Ваш Telegram ID: {message.from_user.id}\n"
            f"Обратитесь к администратору для получения доступа."
        )
        return

    if not user.is_active:
        await message.answer(
            " Ваш аккаунт еще не активирован.\n"
            f"Ваш Telegram ID: {user.telegram_id}\n"
            "Обратитесь к администратору для получения доступа."
        )
        return

    # Показываем главное меню в зависимости от роли
    keyboard = get_main_menu(user.role)

    welcome_text = f" Добро пожаловать, {user.full_name}!\n\n"

    if user.role == UserRole.ADMIN:
        welcome_text += " Вы вошли как Администратор"
    elif user.role == UserRole.WAREHOUSE:
        welcome_text += " Вы вошли как Сотрудник склада"
    elif user.role == UserRole.OPERATOR:
        welcome_text += " Вы вошли как Оператор"
    elif user.role == UserRole.DRIVER:
        welcome_text += " Вы вошли как Водитель"

    await message.answer(welcome_text, reply_markup=keyboard)

@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery, session: AsyncSession):
    """Возврат в главное меню"""

    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()

    if user and user.is_active:
        keyboard = get_main_menu(user.role)
        await callback.message.edit_text(
            " Главное меню",
            reply_markup=keyboard
        )

    await callback.answer()



@router.message(Command("role"))
async def change_my_role(message: Message, session: AsyncSession):
    """Команда для быстрой смены роли (для тестирования)"""
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer(" Вы не зарегистрированы в системе")
        return
    
    # Клавиатура выбора роли
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Администратор", callback_data="test_role:admin")],
        [InlineKeyboardButton(text=" Склад", callback_data="test_role:warehouse")],
        [InlineKeyboardButton(text=" Оператор", callback_data="test_role:operator")],
        [InlineKeyboardButton(text=" Водитель", callback_data="test_role:driver")],
    ])
    
    await message.answer(
        f" <b>Смена роли для тестирования</b>\n\n"
        f"Текущая роль: {user.role.value}\n"
        f"Выберите новую роль:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("test_role:"))
async def set_test_role(callback: CallbackQuery, session: AsyncSession):
    """Установить тестовую роль"""
    role_name = callback.data.split(":")[1]
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return
    
    # Меняем роль
    role_map = {
        "admin": UserRole.ADMIN,
        "warehouse": UserRole.WAREHOUSE,
        "operator": UserRole.OPERATOR,
        "driver": UserRole.DRIVER
    }
    
    user.role = role_map[role_name]
    await session.commit()
    
    await callback.answer(f" Роль изменена на {user.role.value}")
    
    # Показываем новое главное меню
    keyboard = get_main_menu(user.role)
    await callback.message.edit_text(
        f" <b>Роль изменена!</b>\n\n"
        f"Новая роль: {user.role.value}\n\n"
        f"Главное меню:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


