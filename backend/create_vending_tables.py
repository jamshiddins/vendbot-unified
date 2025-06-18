import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from db.models import Base
import os
from dotenv import load_dotenv

load_dotenv()

async def create_tables():
    print("Создание таблиц для вендинга...")
    
    engine = create_async_engine(os.getenv("DATABASE_URL"))
    
    async with engine.begin() as conn:
        # Создаем таблицы
        await conn.run_sync(Base.metadata.create_all)
        print(" Таблицы созданы успешно!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())
