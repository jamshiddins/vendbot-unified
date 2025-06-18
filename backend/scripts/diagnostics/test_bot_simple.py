import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

BOT_TOKEN = "7435657487:AAGiKh4x41v6VupkvvB5qKdcEQCeeXewszk"

dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(" Бот работает!")

async def main():
    bot = Bot(token=BOT_TOKEN)
    print(" Бот запущен! Нажмите Ctrl+C для остановки")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
