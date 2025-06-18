import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
import asyncpg

async def test_supabase():
    # Получаем URL из окружения
    db_url = os.getenv("DATABASE_URL")
    print(f"Original URL: {db_url[:50]}...")
    
    # Конвертируем для asyncpg
    if db_url.startswith("postgresql://"):
        async_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        print(f"Converted URL: {async_url[:50]}...")
    else:
        async_url = db_url
    
    # Тест 1: Прямое подключение через asyncpg
    print("\n=== Test 1: Direct asyncpg connection ===")
    try:
        # Парсим URL для asyncpg
        conn_str = db_url.replace("postgresql://", "")
        conn = await asyncpg.connect(f"postgresql://{conn_str}")
        version = await conn.fetchval('SELECT version()')
        print(f" Direct connection OK: {version[:50]}...")
        await conn.close()
    except Exception as e:
        print(f" Direct connection failed: {e}")
    
    # Тест 2: SQLAlchemy подключение
    print("\n=== Test 2: SQLAlchemy connection ===")
    engine = create_async_engine(async_url, echo=True)
    try:
        async with engine.connect() as conn:
            result = await conn.execute("SELECT current_database()")
            db_name = result.scalar()
            print(f" SQLAlchemy connection OK: {db_name}")
    except Exception as e:
        print(f" SQLAlchemy connection failed: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_supabase())
