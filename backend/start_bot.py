import asyncio
import os
import sys
import time
from sqlalchemy.ext.asyncio import create_async_engine

async def main():
    print("=== Starting VendBot ===")
    
    # Проверяем переменные
    db_url = os.getenv("DATABASE_URL", "")
    bot_token = os.getenv("BOT_TOKEN", "")
    
    if not bot_token:
        print(" BOT_TOKEN not set!")
        sys.exit(1)
        
    if not db_url:
        print(" DATABASE_URL not set!")
        sys.exit(1)
    
    print(f" BOT_TOKEN: ...{bot_token[-10:]}")
    print(f" DATABASE_URL: {db_url[:30]}...")
    
    # Импортируем и запускаем бота
    try:
        from bot.main import main as bot_main
        await bot_main()
    except Exception as e:
        print(f" Error starting bot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
