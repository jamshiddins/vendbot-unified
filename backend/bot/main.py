import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

from core.config import settings
from db.database import init_db, get_db_session
from bot.handlers import setup_handlers
from bot.middlewares import setup_middlewares

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logger.info("Запуск бота...")
    
    # Инициализация БД
    await init_db()
    logger.info("База данных инициализирована")
    
    # Уведомление админов
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                " Бот запущен и готов к работе!",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение админу {admin_id}: {e}")

async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("Остановка бота...")
    
    # Уведомление админов
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                " Бот остановлен",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение админу {admin_id}: {e}")

async def main():
    """Основная функция запуска бота"""
    # Создание бота с parse_mode без DefaultBotProperties
    bot = Bot(token=settings.bot_token)
    
    # Создание диспетчера
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация middleware
    setup_middlewares(dp)
    
    # Регистрация handlers
    setup_handlers(dp)
    
    # Регистрация функций запуска/остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Запуск бота
    try:
        logger.info("Начинаем polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
