from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from core.config import settings
from .handlers import setup_handlers
from .middlewares import setup_middlewares
import logging

logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.bot = None
        self.dp = None
        self.webhook_handler = None
    
    async def start(self):
        """Запуск бота"""
        # Инициализация бота
        self.bot = Bot(token=settings.BOT_TOKEN)
        
        # Инициализация диспетчера с Redis хранилищем
        storage = RedisStorage.from_url(settings.REDIS_URL)
        self.dp = Dispatcher(storage=storage)
        
        # Настройка обработчиков и middleware
        setup_handlers(self.dp)
        setup_middlewares(self.dp)
        
        # Настройка вебхука если указан URL
        if settings.WEBHOOK_URL:
            await self.setup_webhook()
        else:
            # Запуск polling для локальной разработки
            logger.info("Starting bot in polling mode...")
            await self.dp.start_polling(self.bot)
    
    async def setup_webhook(self):
        """Настройка вебхука"""
        webhook_url = f"{settings.WEBHOOK_URL}/webhook"
        await self.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
    
    async def stop(self):
        """Остановка бота"""
        if self.bot:
            await self.bot.session.close()
            if settings.WEBHOOK_URL:
                await self.bot.delete_webhook()

bot_manager = BotManager()