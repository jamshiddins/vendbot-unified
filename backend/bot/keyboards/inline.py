from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db.models import User

def get_users_list_keyboard(users: list[User]) -> InlineKeyboardMarkup:
    '''Клавиатура со списком пользователей'''
    buttons = []
    
    for user in users:
        status = '' if user.is_active else ''
        roles = f" ({', '.join(user.roles)})" if user.roles else ""
        
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {user.full_name}{roles}",
                callback_data=f"user_role:{user.telegram_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text=" Назад", callback_data="back_to_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_role_selection_keyboard(user_id: int, current_roles: list[str]) -> InlineKeyboardMarkup:
    '''Клавиатура выбора ролей'''
    roles = [
        ('admin', ' Администратор'),
        ('warehouse', '📦 Склад'),
        ('operator', '👷 Оператор'),
        ('driver', ' Водитель')
    ]
    
    buttons = []
    
    # Кнопки ролей
    for role_key, role_name in roles:
        if role_key in current_roles:
            text = f" {role_name}"
        else:
            text = f" {role_name}"
        
        buttons.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"toggle_role:{user_id}:{role_key}"
            )
        ])
    
    # Кнопка активации/деактивации
    buttons.append([
        InlineKeyboardButton(
            text=" Активировать" if user_id != 42283329 else " Деактивировать",
            callback_data=f"toggle_active:{user_id}"
        )
    ])
    
    # Кнопка назад
    buttons.append([
        InlineKeyboardButton(
            text=" К списку пользователей",
            callback_data="cmd_role"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_menu(user: User) -> InlineKeyboardMarkup:
    '''Главное меню в зависимости от ролей пользователя'''
    buttons = []
    
    # Для владельца - специальная кнопка
    if user.telegram_id == 42283329:
        buttons.append([
            InlineKeyboardButton(
                text=" Управление ролями",
                callback_data="cmd_role"
            )
        ])
    
    # Кнопки по ролям
    if user.has_role('admin'):
        buttons.extend([
            [InlineKeyboardButton(text=" Пользователи", callback_data="admin_users")],
            [InlineKeyboardButton(text=" Автоматы", callback_data="admin_machines")],
            [InlineKeyboardButton(text=" Отчеты", callback_data="admin_reports")]
        ])
    
    if user.has_role('warehouse'):
        buttons.extend([
            [InlineKeyboardButton(text=" Склад", callback_data="warehouse_inventory")],
            [InlineKeyboardButton(text=" Бункеры", callback_data="warehouse_hoppers")]
        ])
    
    if user.has_role('operator'):
        buttons.extend([
            [InlineKeyboardButton(text=" Мои задачи", callback_data="operator_tasks")],
            [InlineKeyboardButton(text=" Обслуживание", callback_data="operator_service")]
        ])
    
    if user.has_role('driver'):
        buttons.extend([
            [InlineKeyboardButton(text=" Маршруты", callback_data="driver_routes")],
            [InlineKeyboardButton(text=" Доставки", callback_data="driver_deliveries")]
        ])
    
    # Общие кнопки
    buttons.append([
        InlineKeyboardButton(text=" Профиль", callback_data="profile")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
