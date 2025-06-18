from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.models import UserRole

def get_main_menu(role: UserRole) -> InlineKeyboardMarkup:
    """Главное меню в зависимости от роли"""
    
    if role == UserRole.ADMIN:
        keyboard = [
            [InlineKeyboardButton(text=" Пользователи", callback_data="admin_users")],
            [InlineKeyboardButton(text=" Автоматы", callback_data="admin_machines")],
            [InlineKeyboardButton(text=" Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton(text=" Настройки", callback_data="admin_settings")],
        ]
    elif role == UserRole.WAREHOUSE:
        keyboard = [
            [InlineKeyboardButton(text=" Остатки", callback_data="warehouse_stock")],
            [InlineKeyboardButton(text=" Поступление", callback_data="warehouse_receive")],
            [InlineKeyboardButton(text=" Назначить", callback_data="warehouse_assign")],
            [InlineKeyboardButton(text=" Возвраты", callback_data="warehouse_returns")],
        ]
    elif role == UserRole.OPERATOR:
        keyboard = [
            [InlineKeyboardButton(text=" Мои задания", callback_data="operator_tasks")],
            [InlineKeyboardButton(text=" Мои автоматы", callback_data="operator_machines")],
            [InlineKeyboardButton(text=" Установить", callback_data="operator_install")],
            [InlineKeyboardButton(text=" Снять", callback_data="operator_remove")],
        ]
    elif role == UserRole.DRIVER:
        keyboard = [
            [InlineKeyboardButton(text=" Начать поездку", callback_data="driver_start_trip")],
            [InlineKeyboardButton(text=" Заправка", callback_data="driver_fuel")],
            [InlineKeyboardButton(text=" История", callback_data="driver_history")],
        ]
    else:
        keyboard = []
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_button(callback_data: str = "main_menu") -> InlineKeyboardMarkup:
    """Кнопка назад"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Назад", callback_data=callback_data)]
    ])

def get_cancel_button() -> InlineKeyboardMarkup:
    """Кнопка отмены"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Отмена", callback_data="cancel")]
    ])

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=" Да", callback_data="confirm"),
            InlineKeyboardButton(text=" Нет", callback_data="cancel")
        ]
    ])

