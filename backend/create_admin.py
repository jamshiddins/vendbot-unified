import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from db.models import User, UserRole
import os
from dotenv import load_dotenv

load_dotenv()

async def create_admin():
    engine = create_async_engine(os.getenv("DATABASE_URL"))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Ваш Telegram ID (замените на свой)
        admin_telegram_id = 42283329  # ЗАМЕНИТЕ НА ВАШ TELEGRAM ID
        
        # Проверяем существует ли пользователь
        result = await session.execute(
            select(User).where(User.telegram_id == admin_telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.role = UserRole.ADMIN
            user.is_active = True
            print(f" Пользователь обновлен как администратор")
        else:
            user = User(
                telegram_id=admin_telegram_id,
                username="admin",
                full_name="Администратор",
                role=UserRole.ADMIN,
                is_active=True
            )
            session.add(user)
            print(f" Администратор создан")
        
        await session.commit()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_admin())

