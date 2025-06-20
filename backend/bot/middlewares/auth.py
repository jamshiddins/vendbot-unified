from typing import Callable, Any
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import User

class AuthMiddleware(BaseMiddleware):
    '''Middleware для проверки авторизации и активности'''
    
    async def __call__(
        self,
        handler: Callable,
        event: Message | CallbackQuery,
        data: dict[str, Any]
    ) -> Any:
        session: AsyncSession = data.get('session')
        
        if not session:
            return await handler(event, data)
        
        # Получаем пользователя
        from_user = event.from_user
        result = await session.execute(
            select(User).where(User.telegram_id == from_user.id)
        )
        user = result.scalar_one_or_none()
        
        # Владелец всегда активен
        if from_user.id == 42283329:
            if user:
                user.is_active = True
                if not user.roles or 'admin' not in user.roles:
                    user.add_role('admin')
                await session.commit()
        
        # Проверяем активность для остальных
        if user and not user.is_active and from_user.id != 42283329:
            # Разрешаем только /start для неактивных
            if isinstance(event, Message) and event.text == '/start':
                pass
            else:
                await event.answer(
                    ' <b>Доступ ограничен</b>\n\n'
                    'Ваш аккаунт не активирован.\n'
                    'Обратитесь к администратору для активации.',
                    show_alert=True if isinstance(event, CallbackQuery) else False
                )
                return
        
        # Передаем пользователя дальше
        data['user'] = user
        
        return await handler(event, data)
