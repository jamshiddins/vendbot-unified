from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional
from db.models import User

def get_back_button(callback_data: str = "back") -> InlineKeyboardMarkup:
    """Кнопка назад"""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=" Назад", callback_data=callback_data))
    return keyboard.as_markup()

def get_cancel_button() -> InlineKeyboardMarkup:
    """Кнопка отмены"""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=" Отмена", callback_data="cancel"))
    return keyboard.as_markup()

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text=" Да", callback_data="confirm"),
        InlineKeyboardButton(text=" Нет", callback_data="cancel")
    )
    return keyboard.as_markup()

def get_main_menu(user: Optional[User] = None) -> InlineKeyboardMarkup:
    """Создает главное меню бота с учетом роли пользователя"""
    keyboard = InlineKeyboardBuilder()
    
    # Базовые кнопки для всех
    keyboard.row(
        InlineKeyboardButton(text=" Профиль", callback_data="profile"),
        InlineKeyboardButton(text=" Статистика", callback_data="stats")
    )
    
    # Дополнительные кнопки в зависимости от роли
    if user and hasattr(user, "roles"):
        if "admin" in user.roles:
            keyboard.row(
                InlineKeyboardButton(text=" Пользователи", callback_data="admin_users"),
                InlineKeyboardButton(text=" Настройки", callback_data="admin_settings")
            )
        
        if "warehouse" in user.roles:
            keyboard.row(
                InlineKeyboardButton(text=" Склад", callback_data="warehouse_menu")
            )
        
        if "operator" in user.roles:
            keyboard.row(
                InlineKeyboardButton(text=" Мои задачи", callback_data="operator_tasks")
            )
        
        if "driver" in user.roles:
            keyboard.row(
                InlineKeyboardButton(text=" Маршруты", callback_data="driver_routes")
            )
    
    keyboard.row(
        InlineKeyboardButton(text=" Помощь", callback_data="help"),
        InlineKeyboardButton(text="ℹ О боте", callback_data="about")
    )
    
    return keyboard.as_markup()

def get_users_list_keyboard(users: List[User]) -> InlineKeyboardMarkup:
    """Клавиатура со списком пользователей"""
    keyboard = InlineKeyboardBuilder()
    
    for user in users[:20]:  # Ограничиваем 20 пользователями
        name = user.full_name or user.username or f"ID: {user.telegram_id}"
        keyboard.row(
            InlineKeyboardButton(
                text=f"{'' if user.is_active else ''} {name}",
                callback_data=f"user:{user.telegram_id}"
            )
        )
    
    if len(users) > 20:
        keyboard.row(
            InlineKeyboardButton(
                text=f"... и еще {len(users) - 20} пользователей",
                callback_data="noop"
            )
        )
    
    keyboard.row(get_back_button("admin_menu"))
    
    return keyboard.as_markup()

def get_role_selection_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора роли для пользователя"""
    keyboard = InlineKeyboardBuilder()
    
    roles = [
        (" Администратор", "admin"),
        (" Склад", "warehouse"),
        (" Оператор", "operator"),
        (" Водитель", "driver")
    ]
    
    for name, role in roles:
        keyboard.row(
            InlineKeyboardButton(
                text=name,
                callback_data=f"set_role:{user_id}:{role}"
            )
        )
    
    keyboard.row(get_back_button("user_list"))
    
    return keyboard.as_markup()

# Экспортируем все функции
__all__ = [
    "get_back_button",
    "get_cancel_button", 
    "get_confirm_keyboard",
    "get_main_menu",
    "get_users_list_keyboard",
    "get_role_selection_keyboard"
]
