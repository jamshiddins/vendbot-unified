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

# Откройте файл в VSCode и добавьте в конец:

def get_main_menu():
    """Создает главное меню бота"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Кнопки главного меню
    buttons = [
        InlineKeyboardButton("👤 Профиль", callback_data="profile"),
        InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
        InlineKeyboardButton("ℹ️ Помощь", callback_data="help"),
    ]
    
    keyboard.add(*buttons)
    
    return keyboard
