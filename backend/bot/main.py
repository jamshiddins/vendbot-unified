import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from redis.asyncio import Redis

from core.config import settings
from bot.handlers import start, admin, warehouse, operator, admin_machines, hopper_management
from bot.middlewares.database import DatabaseMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция бота"""

    logger.info("Инициализация бота...")

    # Создаем движок БД
    engine = create_async_engine(settings.database_url)
    session_pool = async_sessionmaker(engine, expire_on_commit=False)

    # Создаем Redis
    redis = Redis.from_url(settings.redis_url)
    storage = RedisStorage(redis=redis)

    # Создаем бота и диспетчер
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=storage)
    
    # Регистрируем middleware
    dp.message.middleware(DatabaseMiddleware(session_pool))
    dp.callback_query.middleware(DatabaseMiddleware(session_pool))
    
    # Регистрируем роутеры
    logger.info("Регистрация handlers...")
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(admin_machines.router)
    dp.include_router(warehouse.router)
    dp.include_router(operator.router)
    dp.include_router(hopper_management.router)

    # Запускаем бота
    logger.info(" Бот запущен и готов к работе")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await engine.dispose()
        await redis.close()

if __name__ == "__main__":
    asyncio.run(main())


