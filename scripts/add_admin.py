import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import text, select
from db.database import engine, AsyncSessionLocal
from db.models import User, UserRole
from core.config import settings
from datetime import datetime

async def add_admin():
    '''Добавить админа в БД'''
    async with AsyncSessionLocal() as session:
        # Проверяем есть ли уже админ
        result = await session.execute(
            select(User).where(User.telegram_id == 42283329)
        )
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            # Добавляем админа
            admin = User(
                telegram_id=42283329,
                username='Jamshiddin',
                full_name='',
                role=UserRole.ADMIN,
                is_active=True
            )
            session.add(admin)
            await session.commit()
            print(' Админ добавлен в БД')
        else:
            # Обновляем роль на админа
            existing_user.role = UserRole.ADMIN
            existing_user.is_active = True
            await session.commit()
            print(' Роль обновлена на админа')
            
    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(add_admin())
