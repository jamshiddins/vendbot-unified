﻿from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class DatabaseMiddleware(BaseMiddleware):
    """Middleware для работы с базой данных"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Здесь можно добавить сессию БД в data
        return await handler(event, data)
