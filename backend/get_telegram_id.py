import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot

load_dotenv()

async def get_updates():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    updates = await bot.get_updates()
    
    print("=== Последние обновления ===")
    for update in updates[-5:]:  # Последние 5 обновлений
        if update.message and update.message.from_user:
            print(f"ID: {update.message.from_user.id}")
            print(f"Username: @{update.message.from_user.username}")
            print(f"Name: {update.message.from_user.full_name}")
            print("-" * 30)
    
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(get_updates())
