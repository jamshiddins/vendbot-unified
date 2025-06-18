import os
import sys
sys.path.insert(0, '/app/backend')

print("=== Environment Check ===")
db_from_env = os.getenv('DATABASE_URL', 'NOT SET')
print(f"DATABASE_URL from env: {db_from_env[:50] if db_from_env != 'NOT SET' else 'NOT SET'}...")

print("\n=== Config Check ===")
from core.config import settings
print(f"settings.database_url: {settings.database_url[:50]}...")

print("\n=== Testing Connection ===")
import asyncio
from sqlalchemy import text
from db.database import engine

async def test():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f" Connected to: {version}")
            
            # Проверим таблицы
            result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            tables = result.fetchall()
            print(f"\n Tables in database: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
                
    except Exception as e:
        print(f" Connection failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

asyncio.run(test())
