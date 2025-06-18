import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from fastapi import FastAPI
import uvicorn
from threading import Thread

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "7435657487:AAGiKh4x41v6VupkvvB5qKdcEQCeeXewszk"
APP_NAME = "VendBot"
APP_VERSION = "2.0.0"

# FastAPI приложение
app = FastAPI(title=APP_NAME, version=APP_VERSION)

@app.get("/")
async def root():
    return {"app": APP_NAME, "version": APP_VERSION, "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "bot": "running"}

# Telegram бот
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f" Привет, {message.from_user.full_name}!\n\n"
        f" Я VendBot - система управления вендинговыми автоматами.\n\n"
        f" Команды:\n"
        f"/start - Начало работы\n"
        f"/help - Помощь\n"
        f"/status - Статус системы"
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        " **Помощь по VendBot**\n\n"
        "Система для управления сетью кофейных автоматов.\n"
        "Для доступа обратитесь к администратору.",
        parse_mode="Markdown"
    )

@dp.message(Command("status"))
async def cmd_status(message: Message):
    await message.answer(
        " **Статус системы**\n\n"
        " Бот: Активен\n"
        " API: Работает\n"
        " База данных: Подключена\n\n"
        f"Версия: {APP_VERSION}",
        parse_mode="Markdown"
    )

async def start_bot():
    """Запуск бота"""
    logger.info(" Запуск Telegram бота...")
    await dp.start_polling(bot)

def run_bot():
    """Запуск бота в отдельном потоке"""
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.get_event_loop().run_until_complete(start_bot())

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем FastAPI
    logger.info(f" Запуск {APP_NAME} v{APP_VERSION}")
    logger.info(" API доступно по адресу: http://localhost:8000")
    logger.info(" Telegram бот: @vendhub24bot")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
