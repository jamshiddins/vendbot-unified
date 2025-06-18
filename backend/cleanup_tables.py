import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv

load_dotenv()

async def cleanup_old_tables():
    print("Очистка старых таблиц...")
    
    engine = create_async_engine(os.getenv("DATABASE_URL"))
    
    async with engine.begin() as conn:
        # Удаляем старую таблицу hopper_operations если есть
        await conn.execute(text("DROP TABLE IF EXISTS hopper_operations CASCADE"))
        # Переименовываем новую
        await conn.execute(text("ALTER TABLE IF EXISTS hopper_operations_new RENAME TO hopper_operations"))
        print(" Очистка завершена!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(cleanup_old_tables())
