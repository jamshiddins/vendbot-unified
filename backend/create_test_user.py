import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from db.models import User, UserRole
import os
from dotenv import load_dotenv

load_dotenv()

async def create_test_user():
    engine = create_async_engine(os.getenv("DATABASE_URL"))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Создаем тестового пользователя
        test_user = User(
            telegram_id=111111111,
            username="test_operator",
            full_name="Тестовый Оператор",
            role=UserRole.OPERATOR,
            is_active=False
        )
        session.add(test_user)
        
        await session.commit()
        print(" Тестовый пользователь создан")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_test_user())
