import asyncio
import os
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импорты из нашего проекта
try:
    from core.config import settings
    from db.database import init_db
    from bot.handlers import setup_handlers
    from bot.middlewares.database import DatabaseMiddleware
    from bot.middlewares.logging import LoggingMiddleware
except ImportError as e:
    logger.error(f"Ошибка импорта: {e}")
    logger.error(f"PYTHONPATH: {sys.path}")
    sys.exit(1)

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logger.info(" Запуск бота...")
    
    # Инициализация БД
    try:
        await init_db()
        logger.info(" База данных инициализирована")
    except Exception as e:
        logger.error(f" Ошибка инициализации БД: {e}")
        raise
    
    # Информация о боте
    bot_info = await bot.get_me()
    logger.info(f" Бот @{bot_info.username} запущен!")

async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info(" Остановка бота...")
    await bot.session.close()

async def main():
    """Основная функция запуска бота"""
    # Проверка токена
    if not (hasattr(settings, 'BOT_TOKEN') and settings.BOT_TOKEN) and not (hasattr(settings, 'bot_token') and settings.bot_token):
        logger.error(" BOT_TOKEN не установлен!")
        sys.exit(1)
    
    # Создание бота с parse_mode по умолчанию
    bot = Bot(token=getattr(settings, 'bot_token', None) or getattr(settings, 'BOT_TOKEN', None) or os.getenv('BOT_TOKEN'), parse_mode="HTML")
    
    # Создание диспетчера
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация middleware
    dp.message.middleware(DatabaseMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    # Регистрация хендлеров
    setup_handlers(dp)
    
    # Регистрация startup/shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Запуск
    try:
        logger.info(" Бот запущен и готов к работе!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f" Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info(" Бот остановлен пользователем")
    except Exception as e:
        logger.error(f" Непредвиденная ошибка: {e}")
        sys.exit(1)

