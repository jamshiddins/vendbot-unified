import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загружаем конфигурацию из .env
TOKEN = None
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('BOT_TOKEN='):
                TOKEN = line.strip().split('=', 1)[1]
                break
except Exception as e:
    logger.error(f"Ошибка чтения .env: {e}")

if not TOKEN:
    logger.error(" BOT_TOKEN не найден в .env!")
    exit(1)

# Создаем бота
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_name = message.from_user.full_name
    await message.answer(
        f" Привет, {user_name}!\n\n"
        f" Я VendBot - система управления вендинговыми автоматами.\n\n"
        f" Доступные команды:\n"
        f"/start - Начало работы\n"
        f"/help - Помощь\n"
        f"/status - Статус системы"
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        " **Помощь по VendBot**\n\n"
        "Это система для управления сетью кофейных автоматов.\n\n"
        "Для получения доступа к функциям системы обратитесь к администратору.",
        parse_mode="Markdown"
    )

@dp.message(Command("status"))
async def cmd_status(message: Message):
    await message.answer(
        " **Статус системы**\n\n"
        " Бот: Активен\n"
        " База данных: Подключена\n"
        " API: В разработке\n\n"
        f"Версия: 2.0.0",
        parse_mode="Markdown"
    )

async def main():
    logger.info(" Запуск VendBot...")
    logger.info(f" Токен бота: {TOKEN[:20]}...")
    
    # Получаем информацию о боте
    bot_info = await bot.get_me()
    logger.info(f" Бот запущен: @{bot_info.username}")
    logger.info(" Отправьте /start боту в Telegram")
    
    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info(" Бот остановлен")
