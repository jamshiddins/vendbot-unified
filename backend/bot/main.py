import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from core.config import settings
from db.database import engine
from bot.handlers import start, admin, warehouse, operator, driver, common, owner
from bot.middlewares.auth import AuthMiddleware
from bot.middlewares.logging import LoggingMiddleware
from bot.middlewares.database import DatabaseMiddleware

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    '''Главная функция запуска бота'''
    logger.info(' Запуск VendBot...')
    
    # Создаем бота
    bot = Bot(token=settings.bot_token, parse_mode='HTML')
    
    # Временно используем MemoryStorage
    storage = MemoryStorage()
    
    # Создаем диспетчер
    dp = Dispatcher(storage=storage)
    
    # Регистрируем middleware
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    # Регистрируем роутеры
    dp.include_router(start.router)
    dp.include_router(owner.router)  # Роутер владельца
    dp.include_router(admin.router)
    dp.include_router(warehouse.router)
    dp.include_router(operator.router)
    dp.include_router(driver.router)
    dp.include_router(common.router)
    
    # Уведомляем владельца о запуске
    try:
        await bot.send_message(
            42283329,
            ' VendBot запущен и готов к работе!\n\n'
            'Используйте /role для управления пользователями.'
        )
    except Exception as e:
        logger.error(f'Не удалось отправить сообщение владельцу: {e}')
    
    logger.info(' Бот успешно запущен')
    
    try:
        # Запускаем polling
        await dp.start_polling(bot)
    finally:
        # Закрываем соединения
        await bot.session.close()
        await engine.dispose()

if __name__ == '__main__':
    asyncio.run(main())
