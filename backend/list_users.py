import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from db.models import User
import os
from dotenv import load_dotenv

load_dotenv()

async def list_users():
    engine = create_async_engine(os.getenv("DATABASE_URL"))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        print("=== Пользователи в БД ===")
        for user in users:
            print(f"ID: {user.telegram_id}")
            print(f"Username: @{user.username}")
            print(f"Name: {user.full_name}")
            print(f"Role: {user.role.value}")
            print(f"Active: {user.is_active}")
            print("-" * 30)
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(list_users())
