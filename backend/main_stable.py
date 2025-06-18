"""
VendBot v2.0 - Enterprise Vending Management System
"""
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from threading import Thread

# Загружаем конфигурацию
try:
    from core.config import settings
    CONFIG_LOADED = True
except Exception as e:
    print(f" Использую минимальную конфигурацию: {e}")
    CONFIG_LOADED = False
    
    class Settings:
        APP_NAME = "VendBot"
        APP_VERSION = "2.0.0"
        BOT_TOKEN = "7435657487:AAGiKh4x41v6VupkvvB5qKdcEQCeeXewszk"
        ENVIRONMENT = "development"
        DEBUG = True
        CORS_ORIGINS = ["http://localhost:3000"]
    
    settings = Settings()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем необходимые директории
for dir_path in ["logs", "uploads/photos", "uploads/documents"]:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

# FastAPI приложение
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-grade vending machine management system"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if CONFIG_LOADED else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API эндпоинты
@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "telegram_bot": True,
            "web_api": True,
            "database": CONFIG_LOADED,
            "redis": CONFIG_LOADED
        }
    }

@app.get("/api/v2/health")
async def health():
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "bot": "running",
            "database": "connected" if CONFIG_LOADED else "not configured",
            "redis": "connected" if CONFIG_LOADED else "not configured"
        }
    }

@app.get("/api/v2/stats")
async def stats():
    return {
        "machines": 16,
        "hoppers": 160,
        "operators": 12,
        "drivers": 4,
        "warehouse_staff": 3,
        "active_routes": 2
    }

# Telegram бот
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start"""
    user_name = message.from_user.full_name or message.from_user.username or "Пользователь"
    
    await message.answer(
        f" <b>Добро пожаловать в VendBot!</b>\n\n"
        f" Я - система управления вендинговыми автоматами.\n\n"
        f"<b>Ваши данные:</b>\n"
        f" Имя: {user_name}\n"
        f" ID: {message.from_user.id}\n"
        f" Username: @{message.from_user.username or 'не указан'}\n\n"
        f" Используйте /help для списка команд\n"
        f" Или /menu для главного меню",
        parse_mode="HTML"
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Команда /help"""
    help_text = """
<b> Справка по VendBot</b>

<b> Основные команды:</b>
/start - Начало работы
/help - Эта справка
/status - Статус системы
/menu - Главное меню

<b> Команды по ролям:</b>
/admin - Панель администратора
/warehouse - Меню склада
/operator - Меню оператора
/driver - Меню водителя

<b> Информация:</b>
/stats - Статистика системы
/about - О системе

<b> Совет:</b>
Для получения роли обратитесь к администратору системы.
"""
    await message.answer(help_text, parse_mode="HTML")

@dp.message(Command("status"))
async def cmd_status(message: Message):
    """Команда /status"""
    status_text = f"""
<b> Статус системы VendBot</b>

<b>Версия:</b> {settings.APP_VERSION}
<b>Окружение:</b> {settings.ENVIRONMENT}

<b> Сервисы:</b>
- Telegram бот:  Активен
- Web API:  Работает
- База данных: {' Подключена' if CONFIG_LOADED else ' Не настроена'}
- Redis: {' Подключен' if CONFIG_LOADED else ' Не настроен'}

<b> Показатели:</b>
- Время работы: {datetime.now().strftime('%H:%M:%S')}
- Обработано команд: в этой сессии

<b> API:</b>
http://localhost:8000
"""
    await message.answer(status_text, parse_mode="HTML")

@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    """Главное меню"""
    menu_text = """
<b> Главное меню VendBot</b>

Выберите вашу роль:

<b> Администратор</b>
/admin - Панель управления

<b> Склад</b>
/warehouse - Складские операции

<b> Оператор</b>
/operator - Обслуживание машин

<b> Водитель</b>
/driver - Управление маршрутами

<b> Общее</b>
/stats - Статистика
/profile - Мой профиль
/settings - Настройки
"""
    await message.answer(menu_text, parse_mode="HTML")

@dp.message(Command("about"))
async def cmd_about(message: Message):
    """О системе"""
    about_text = f"""
<b> О системе VendBot</b>

<b>{settings.APP_NAME}</b> - это комплексная система управления сетью вендинговых автоматов корпоративного уровня.

<b> Возможности:</b>
- Учет 16 кофейных автоматов
- Управление 160 бункерами
- Контроль остатков ингредиентов
- Маршрутизация водителей
- Фотофиксация операций
- Аналитика и отчетность

<b> Технологии:</b>
- Python + AsyncIO
- Telegram Bot API (aiogram)
- FastAPI + WebSocket
- PostgreSQL + Redis
- Docker + Kubernetes ready

<b> Поддержка:</b>
@vendbot_support

<i>Версия {settings.APP_VERSION}</i>
"""
    await message.answer(about_text, parse_mode="HTML")

# Функция запуска бота
async def start_bot():
    """Запуск Telegram бота"""
    logger.info(" Инициализация Telegram бота...")
    
    try:
        # Информация о боте
        bot_info = await bot.get_me()
        logger.info(f" Бот запущен: @{bot_info.username}")
        
        # Запуск polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f" Ошибка запуска бота: {e}")
        # Пробуем запустить без установки команд
        try:
            await dp.start_polling(bot)
        except Exception as e2:
            logger.error(f" Критическая ошибка: {e2}")

def run_bot_thread():
    """Запуск бота в отдельном потоке"""
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
    logger.info(f" Окружение: {settings.ENVIRONMENT}")
    logger.info(f" Debug режим: {settings.DEBUG}")
    logger.info("="*60)
    
    # Запускаем бота в отдельном потоке
    bot_thread = Thread(target=run_bot_thread, daemon=True)
    bot_thread.start()
    
    # Ждем немного для инициализации бота
    import time
    time.sleep(2)
    
    # Запускаем FastAPI
    logger.info(" Запуск Web API...")
    logger.info(" API доступно: http://localhost:8000")
    logger.info(" Документация: http://localhost:8000/docs")
    logger.info("="*60)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info(" Остановка по запросу пользователя")
