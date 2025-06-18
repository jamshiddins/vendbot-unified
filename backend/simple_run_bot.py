import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

load_dotenv()

# Простой handler для теста
async def cmd_start(message: Message):
    await message.answer(" Привет! Бот работает!")

async def main():
    # Создаем бота
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    
    # Регистрируем handler
    dp.message.register(cmd_start, CommandStart())
    
    # Запускаем
    print(" Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
