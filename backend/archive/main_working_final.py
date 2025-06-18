"""
VendBot - Рабочая версия без set_my_commands
"""
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from threading import Thread

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv(override=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
class Settings(BaseSettings):
    APP_NAME: str = "VendBot"
    APP_VERSION: str = "2.0.0"
    BOT_TOKEN: str = "7435657487:AAGiKh4x41v6VupkvvB5qKdcEQCeeXewszk"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+asyncpg://vendbot:vendbot123@localhost:5432/vendbot"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "your-secret-key"
    JWT_SECRET_KEY: str = "your-jwt-secret"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Состояния для FSM
class UserStates(StatesGroup):
    waiting_for_feedback = State()

# FastAPI приложение
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="VendBot API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Telegram бот
storage = MemoryStorage()
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=storage)

# Inline клавиатуры
def get_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text=" Администратор", callback_data="role_admin"),
            InlineKeyboardButton(text=" Склад", callback_data="role_warehouse")
        ],
        [
            InlineKeyboardButton(text=" Статистика", callback_data="show_stats"),
            InlineKeyboardButton(text="ℹ О системе", callback_data="about")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text=" Назад в меню", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Обработчики команд
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_name = message.from_user.full_name or message.from_user.username or "Пользователь"
    
    await message.answer(
        f" <b>Добро пожаловать в VendBot!</b>\n\n"
        f" Я - система управления вендинговыми автоматами.\n\n"
        f"<b>Ваши данные:</b>\n"
        f" Имя: {user_name}\n"
        f" ID: {message.from_user.id}\n\n"
        f"Выберите действие:",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        " <b>Справка по VendBot</b>\n\n"
        "<b>Команды:</b>\n"
        "/start - Начало работы\n"
        "/help - Эта справка\n"
        "/status - Статус системы\n"
        "/menu - Главное меню",
        parse_mode="HTML"
    )

@dp.message(Command("status"))
async def cmd_status(message: Message):
    await message.answer(
        f" <b>Статус системы</b>\n\n"
        f"Версия: {settings.APP_VERSION}\n"
        f"Окружение: {settings.ENVIRONMENT}\n"
        f"Бот:  Активен\n"
        f"API:  Работает",
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )

@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        " <b>Главное меню</b>",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

# Обработчики callback
@dp.callback_query(F.data == "back_to_main")
async def callback_back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        " <b>Главное меню</b>",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def callback_about(callback: CallbackQuery):
    await callback.message.edit_text(
        f"ℹ <b>О системе VendBot</b>\n\n"
        f"Версия: {settings.APP_VERSION}\n"
        f"Разработчик: VendHub Solutions",
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

# Обработчик всех остальных сообщений
@dp.message()
async def handle_any_message(message: Message):
    await message.answer(
        " Я не понимаю эту команду.\n\n"
        "Используйте /help для списка команд",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

# Функции запуска
async def start_bot():
    logger.info(" Запуск бота...")
    
    try:
        bot_info = await bot.get_me()
        logger.info(f" Бот запущен: @{bot_info.username}")
        
        # Запускаем polling БЕЗ установки команд
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f" Ошибка: {e}")

def run_bot_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_bot())
    except Exception as e:
        logger.error(f" Ошибка в потоке бота: {e}")

# Главная функция
if __name__ == "__main__":
    logger.info("="*60)
    logger.info(f" Запуск {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("="*60)
    
    # Создаем директории
    Path("logs").mkdir(exist_ok=True)
    Path("uploads/photos").mkdir(parents=True, exist_ok=True)
    
    # Запускаем бота
    bot_thread = Thread(target=run_bot_thread, daemon=True)
    bot_thread.start()
    
    # Ждем
    import time
    time.sleep(2)
    
    # Запускаем API
    logger.info(f" API: http://localhost:{settings.API_PORT}")
    logger.info(f" Docs: http://localhost:{settings.API_PORT}/docs")
    logger.info("="*60)
    
    try:
        uvicorn.run(
            app,
            host=settings.API_HOST,
            port=settings.API_PORT,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info(" Остановка...")
