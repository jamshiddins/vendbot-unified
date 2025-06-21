from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

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

def get_main_menu(user=None):
    """Создает главное меню бота с учетом роли пользователя"""
    keyboard = InlineKeyboardBuilder()
    
    # Базовые кнопки для всех
    keyboard.row(
        InlineKeyboardButton(text=" Профиль", callback_data="profile"),
        InlineKeyboardButton(text=" Статистика", callback_data="stats")
    )
    
    # Дополнительные кнопки в зависимости от роли
    if user and hasattr(user, 'role'):
        if user.role in ['admin', 'warehouse', 'operator', 'driver']:
            keyboard.row(
                InlineKeyboardButton(text=" Рабочее место", callback_data=f"workplace_{user.role}")
            )
        
        if user.role == 'admin':
            keyboard.row(
                InlineKeyboardButton(text=" Админ панель", callback_data="admin_panel")
            )
    
    keyboard.row(
        InlineKeyboardButton(text=" Помощь", callback_data="help"),
        InlineKeyboardButton(text="ℹ О боте", callback_data="about")
    )
    
    return keyboard.as_markup()
