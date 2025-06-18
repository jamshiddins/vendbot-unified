"""
VendBot v2.0 - Система управления вендинговыми автоматами
"""
import asyncio
import logging
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from core.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем необходимые директории
Path("logs").mkdir(exist_ok=True)
Path("uploads/photos").mkdir(parents=True, exist_ok=True)

# Инициализация бота
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start"""
    await message.answer(
        f" Привет, {message.from_user.full_name}!\n\n"
        f" Я VendBot v{settings.APP_VERSION} - система управления вендинговыми автоматами.\n\n"
        f" Основные команды:\n"
        f"/start - Начало работы\n"
        f"/help - Помощь\n"
        f"/status - Статус системы\n"
        f"/menu - Главное меню"
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Команда /help"""
    await message.answer(
        " **Справка по VendBot**\n\n"
        "Это корпоративная система для управления сетью кофейных автоматов.\n\n"
        "**Доступные роли:**\n"
        " Администратор - полный доступ\n"
        " Склад - управление запасами\n"
        " Оператор - обслуживание машин\n"
        " Водитель - логистика\n\n"
        "Для получения доступа обратитесь к администратору.",
        parse_mode="Markdown"
    )

@dp.message(Command("status"))
async def cmd_status(message: Message):
    """Команда /status"""
    await message.answer(
        f" **Статус системы VendBot v{settings.APP_VERSION}**\n\n"
        f" Бот: Активен\n"
        f" База данных: Подключена\n"
        f" Конфигурация: OK\n"
        f" API: В разработке\n\n"
        f"**Окружение:** {settings.ENVIRONMENT}\n"
        f"**Debug режим:** {'Да' if settings.DEBUG else 'Нет'}",
        parse_mode="Markdown"
    )

@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    """Главное меню"""
    await message.answer(
        " **Главное меню VendBot**\n\n"
        "Выберите действие:\n\n"
        " /warehouse - Меню склада\n"
        " /operator - Меню оператора\n"
        " /driver - Меню водителя\n"
        " /admin - Админ панель\n\n"
        " /stats - Статистика\n"
        " /help - Помощь",
        parse_mode="Markdown"
    )

async def main():
    """Главная функция"""
    logger.info(f" Запуск {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f" Окружение: {settings.ENVIRONMENT}")
    logger.info(f" Debug режим: {settings.DEBUG}")
    
    # Информация о боте
    bot_info = await bot.get_me()
    logger.info(f" Бот запущен: @{bot_info.username}")
    
    # Запуск polling
    logger.info(" Система готова к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info(" Бот остановлен пользователем")
    except Exception as e:
        logger.error(f" Критическая ошибка: {e}")
