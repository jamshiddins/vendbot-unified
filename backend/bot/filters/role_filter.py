from aiogram.filters import BaseFilter
from aiogram.types import Message
from bot.utils.permissions import OWNER_ID  # Без backend.

class OwnerFilter(BaseFilter):
    """Фильтр для команд, доступных только владельцу"""

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == OWNER_ID
