from aiogram.types import Message, CallbackQuery
from typing import Union

# ID владельца бота - только он может управлять ролями
OWNER_ID = 42283329

async def is_owner(update: Union[Message, CallbackQuery]) -> bool:
    """Проверка, является ли пользователь владельцем"""
    user_id = update.from_user.id if hasattr(update, 'from_user') else None
    return user_id == OWNER_ID

async def can_manage_roles(user_id: int) -> bool:
    """Только владелец может управлять ролями"""
    return user_id == OWNER_ID
