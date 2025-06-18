import os
import sys
sys.path.insert(0, '/app/backend')

print("=== Environment Check ===")
db_from_env = os.getenv('DATABASE_URL', 'NOT SET')
print(f"DATABASE_URL from env: {db_from_env[:50] if db_from_env != 'NOT SET' else 'NOT SET'}...")

print("\n=== Config Check ===")
from core.config import settings
print(f"settings.database_url: {settings.database_url[:50]}...")

print("\n=== Database Module Check ===")
from db.database import engine
print(f"Engine URL: {engine.url}")

print("\n=== Testing Connection ===")
import asyncio

async def test():
    try:
        async with engine.connect() as conn:
            result = await conn.execute("SELECT version()")
            version = result.scalar()
            print(f" Connected to: {version}")
    except Exception as e:
        print(f" Connection failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

asyncio.run(test())
