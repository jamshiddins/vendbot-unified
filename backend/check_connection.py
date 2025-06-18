import os
print("=== Environment Check ===")
print(f"DATABASE_URL from env: {os.getenv('DATABASE_URL', 'NOT SET')[:50]}...")

print("\n=== Config Check ===")
from core.config import settings
print(f"settings.database_url: {settings.database_url[:50]}...")

print("\n=== Testing Connection ===")
import asyncio
from db.database import engine

async def test():
    try:
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            print(" Connection successful!")
    except Exception as e:
        print(f" Connection failed: {e}")
    finally:
        await engine.dispose()

asyncio.run(test())
