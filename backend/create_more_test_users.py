import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from db.models import User, UserRole
import os
from dotenv import load_dotenv

load_dotenv()

async def create_test_users():
    engine = create_async_engine(os.getenv("DATABASE_URL"))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Создаем тестовых пользователей для каждой роли
        test_users = [
            User(
                telegram_id=222222222,
                username="test_warehouse",
                full_name="Тестовый Кладовщик",
                role=UserRole.WAREHOUSE,
                is_active=True
            ),
            User(
                telegram_id=333333333,
                username="test_driver",
                full_name="Тестовый Водитель",
                role=UserRole.DRIVER,
                is_active=True
            ),
        ]
        
        for user in test_users:
            # Проверяем, не существует ли уже
            existing = await session.execute(
                select(User).where(User.telegram_id == user.telegram_id)
            )
            if not existing.scalar_one_or_none():
                session.add(user)
                print(f" Создан: {user.full_name} (ID: {user.telegram_id})")
            else:
                print(f" Уже существует: ID {user.telegram_id}")
        
        await session.commit()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_test_users())
