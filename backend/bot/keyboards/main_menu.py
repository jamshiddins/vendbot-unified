from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db.models.user import UserRole

def get_main_menu(role: UserRole) -> ReplyKeyboardMarkup:
    """Получить главное меню в зависимости от роли"""
    
    if role == UserRole.ADMIN:
        keyboard = [
            [KeyboardButton(text="👥 Пользователи"), KeyboardButton(text="📊 Аналитика")],
            [KeyboardButton(text="🏭 Активы"), KeyboardButton(text="📦 Склад")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="📋 Отчеты")]
        ]
    elif role == UserRole.WAREHOUSE:
        keyboard = [
            [KeyboardButton(text="📦 Склад"), KeyboardButton(text="📥 Приемка")],
            [KeyboardButton(text="📤 Выдача"), KeyboardButton(text="📊 Остатки")],
            [KeyboardButton(text="🔄 Возвраты"), KeyboardButton(text="📋 Отчеты")]
        ]
    elif role == UserRole.OPERATOR:
        keyboard = [
            [KeyboardButton(text="🔧 Обслуживание"), KeyboardButton(text="📦 Бункера")],
            [KeyboardButton(text="📸 Фотоотчет"), KeyboardButton(text="📋 Задания")],
            [KeyboardButton(text="❓ Помощь")]
        ]
    elif role == UserRole.DRIVER:
        keyboard = [
            [KeyboardButton(text="🚛 Маршрут"), KeyboardButton(text="📦 Загрузка")],
            [KeyboardButton(text="✅ Доставка"), KeyboardButton(text="🔄 Возврат")],
            [KeyboardButton(text="⛽ Топливо")]
        ]
    else:
        keyboard = [
            [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="👤 Профиль")]
        ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )