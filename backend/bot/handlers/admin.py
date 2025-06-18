from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from db.models import User, UserRole, Machine, Ingredient, Hopper
from bot.keyboards.inline import get_back_button

router = Router()

def get_user_management_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления пользователями"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Список пользователей", callback_data="users_list")],
        [InlineKeyboardButton(text=" Активировать пользователя", callback_data="user_activate")],
        [InlineKeyboardButton(text=" Деактивировать пользователя", callback_data="user_deactivate")],
        [InlineKeyboardButton(text=" Изменить роль", callback_data="user_change_role")],
        [InlineKeyboardButton(text=" Назад", callback_data="main_menu")]
    ])

def get_users_list_keyboard(users: List[User], action: str) -> InlineKeyboardMarkup:
    """Клавиатура со списком пользователей для выбора"""
    keyboard = []
    for user in users:
        status = "" if user.is_active else ""
        text = f"{status} {user.full_name or user.username or 'ID:' + str(user.telegram_id)}"
        keyboard.append([InlineKeyboardButton(
            text=text, 
            callback_data=f"{action}:{user.id}"
        )])
    keyboard.append([InlineKeyboardButton(text=" Отмена", callback_data="admin_users")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_role_selection_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора роли"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Администратор", callback_data=f"set_role:{user_id}:admin")],
        [InlineKeyboardButton(text=" Склад", callback_data=f"set_role:{user_id}:warehouse")],
        [InlineKeyboardButton(text=" Оператор", callback_data=f"set_role:{user_id}:operator")],
        [InlineKeyboardButton(text=" Водитель", callback_data=f"set_role:{user_id}:driver")],
        [InlineKeyboardButton(text=" Отмена", callback_data="admin_users")]
    ])

@router.callback_query(F.data == "admin_users")
async def show_user_management(callback: CallbackQuery, session: AsyncSession):
    """Показать меню управления пользователями"""
    
    # Проверяем права админа
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    admin = result.scalar_one_or_none()
    
    if not admin or admin.role != UserRole.ADMIN:
        await callback.answer(" Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        " <b>Управление пользователями</b>\n\n"
        "Выберите действие:",
        reply_markup=get_user_management_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "users_list")
async def show_users_list(callback: CallbackQuery, session: AsyncSession):
    """Показать список всех пользователей"""
    
    # Получаем всех пользователей
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    users: List[User] = result.scalars().all()
    
    text = " <b>Список пользователей:</b>\n\n"
    
    for user in users:
        status = "" if user.is_active else ""
        role_emoji = {
            UserRole.ADMIN: "",
            UserRole.WAREHOUSE: "", 
            UserRole.OPERATOR: "",
            UserRole.DRIVER: ""
        }
        
        text += (
            f"{status} {role_emoji.get(user.role, '')} "
            f"<b>{user.full_name or 'Без имени'}</b>\n"
            f"   @{user.username or 'нет'} | ID: {user.telegram_id}\n"
            f"   Роль: {user.role.value}\n"
            f"   Создан: {user.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Назад", callback_data="admin_users")]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "user_activate")
async def show_inactive_users(callback: CallbackQuery, session: AsyncSession):
    """Показать неактивных пользователей для активации"""
    
    # Получаем неактивных пользователей
    result = await session.execute(
        select(User).where(User.is_active == False).order_by(User.created_at.desc())
    )
    users: List[User] = result.scalars().all()
    
    if not users:
        await callback.answer("Все пользователи уже активированы", show_alert=True)
        return
    
    await callback.message.edit_text(
        " <b>Выберите пользователя для активации:</b>",
        reply_markup=get_users_list_keyboard(users, "activate"),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "user_deactivate")
async def show_active_users(callback: CallbackQuery, session: AsyncSession):
    """Показать активных пользователей для деактивации"""
    
    # Получаем активных пользователей (кроме текущего админа)
    result = await session.execute(
        select(User).where(
            User.is_active == True,
            User.telegram_id != callback.from_user.id
        ).order_by(User.created_at.desc())
    )
    users: List[User] = result.scalars().all()
    
    if not users:
        await callback.answer("Нет пользователей для деактивации", show_alert=True)
        return
    
    await callback.message.edit_text(
        " <b>Выберите пользователя для деактивации:</b>",
        reply_markup=get_users_list_keyboard(users, "deactivate"),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "user_change_role")
async def show_users_for_role_change(callback: CallbackQuery, session: AsyncSession):
    """Показать пользователей для изменения роли"""
    
    # Получаем всех пользователей кроме текущего админа
    result = await session.execute(
        select(User).where(
            User.telegram_id != callback.from_user.id
        ).order_by(User.created_at.desc())
    )
    users: List[User] = result.scalars().all()
    
    if not users:
        await callback.answer("Нет пользователей для изменения роли", show_alert=True)
        return
    
    await callback.message.edit_text(
        " <b>Выберите пользователя для изменения роли:</b>",
        reply_markup=get_users_list_keyboard(users, "change_role"),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("activate:"))
async def activate_user(callback: CallbackQuery, session: AsyncSession):
    """Активировать пользователя"""
    user_id = int(callback.data.split(":")[1])
    
    user = await session.get(User, user_id)
    if user:
        user.is_active = True
        await session.commit()
        
        await callback.answer(f" Пользователь {user.full_name or user.username} активирован")
        await show_user_management(callback, session)
    else:
        await callback.answer("Пользователь не найден", show_alert=True)

@router.callback_query(F.data.startswith("deactivate:"))
async def deactivate_user(callback: CallbackQuery, session: AsyncSession):
    """Деактивировать пользователя"""
    user_id = int(callback.data.split(":")[1])
    
    user = await session.get(User, user_id)
    if user:
        user.is_active = False
        await session.commit()
        
        await callback.answer(f" Пользователь {user.full_name or user.username} деактивирован")
        await show_user_management(callback, session)
    else:
        await callback.answer("Пользователь не найден", show_alert=True)

@router.callback_query(F.data.startswith("change_role:"))
async def show_role_selection(callback: CallbackQuery, session: AsyncSession):
    """Показать выбор роли для пользователя"""
    user_id = int(callback.data.split(":")[1])
    
    user = await session.get(User, user_id)
    if user:
        await callback.message.edit_text(
            f" <b>Выберите новую роль для {user.full_name or user.username}:</b>\n"
            f"Текущая роль: {user.role.value}",
            reply_markup=get_role_selection_keyboard(user_id),
            parse_mode="HTML"
        )
    else:
        await callback.answer("Пользователь не найден", show_alert=True)

@router.callback_query(F.data.startswith("set_role:"))
async def set_user_role(callback: CallbackQuery, session: AsyncSession):
    """Установить роль пользователю"""
    _, user_id, role = callback.data.split(":")
    user_id = int(user_id)
    
    user = await session.get(User, user_id)
    if user:
        role_map = {
            "admin": UserRole.ADMIN,
            "warehouse": UserRole.WAREHOUSE,
            "operator": UserRole.OPERATOR,
            "driver": UserRole.DRIVER
        }
        
        user.role = role_map[role]
        await session.commit()
        
        await callback.answer(f" Роль изменена на {user.role.value}")
        await show_user_management(callback, session)
    else:
        await callback.answer("Пользователь не найден", show_alert=True)

# Остальные handlers (machines, stats, settings)
@router.callback_query(F.data == "admin_machines")
async def redirect_to_machines(callback: CallbackQuery):
    """Перенаправить на управление автоматами"""
    from .admin_machines import show_machine_management
    await show_machine_management(callback)

@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery, session: AsyncSession):
    """Показать статистику"""
    
    # Подсчет статистики
    users_count = await session.scalar(select(func.count(User.id)))
    active_users = await session.scalar(
        select(func.count(User.id)).where(User.is_active == True)
    )
    machines_count = await session.scalar(select(func.count(Machine.id)))
    ingredients_count = await session.scalar(select(func.count(Ingredient.id)))
    hoppers_count = await session.scalar(select(func.count(Hopper.id)))
    
    text = (
        " <b>Статистика системы:</b>\n\n"
        f" Пользователей: {users_count} (активных: {active_users})\n"
        f" Автоматов: {machines_count}\n"
        f" Ингредиентов: {ingredients_count}\n"
        f" Бункеров: {hoppers_count}\n"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_settings")
async def show_settings(callback: CallbackQuery, session: AsyncSession):
    """Показать настройки"""
    
    text = (
        " <b>Настройки системы:</b>\n\n"
        " Функция в разработке...\n\n"
        "Здесь будут:\n"
        " Настройки уведомлений\n"
        " Параметры системы\n"
        " Резервное копирование\n"
        " Экспорт данных"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()

__all__ = ["router"]

