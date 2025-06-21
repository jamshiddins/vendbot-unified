from aiogram import Dispatcher
from aiogram.middleware import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject

from db.database import get_db_session
from core.config import settings

class DatabaseMiddleware(BaseMiddleware):
    """Middleware для добавления сессии БД в хендлеры"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with get_db_session() as session:
            data["session"] = session
            return await handler(event, data)

class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Простое логирование
        return await handler(event, data)

def setup_middlewares(dp: Dispatcher):
    """Регистрация всех middleware"""
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    
    if settings.debug:
        dp.message.middleware(LoggingMiddleware())
        dp.callback_query.middleware(LoggingMiddleware())
