import asyncio
import os
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# ��������� �����������
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ������� �� ������ �������
try:
    from core.config import settings
    from db.database import init_db
    from bot.handlers import setup_handlers
    from bot.middlewares.database import DatabaseMiddleware
    from bot.middlewares.logging import LoggingMiddleware
except ImportError as e:
    logger.error(f"������ �������: {e}")
    logger.error(f"PYTHONPATH: {sys.path}")
    sys.exit(1)

async def on_startup(bot: Bot):
    """�������� ��� ������� ����"""
    logger.info(" ������ ����...")
    
    # ������������� ��
    try:
        await init_db()
        logger.info(" ���� ������ ����������������")
    except Exception as e:
        logger.error(f" ������ ������������� ��: {e}")
        raise
    
    # ���������� � ����
    bot_info = await bot.get_me()
    logger.info(f" ��� @{bot_info.username} �������!")

async def on_shutdown(bot: Bot):
    """�������� ��� ��������� ����"""
    logger.info(" ��������� ����...")
    await bot.session.close()

async def main():
    """�������� ������� ������� ����"""
    # �������� ������
    if not (hasattr(settings, 'BOT_TOKEN') and settings.BOT_TOKEN) and not (hasattr(settings, 'bot_token') and settings.bot_token):
        logger.error(" BOT_TOKEN �� ����������!")
        sys.exit(1)
    
    # �������� ���� � parse_mode �� ���������
    bot = Bot(token=getattr(settings, 'bot_token', None) or getattr(settings, 'BOT_TOKEN', None) or os.getenv('BOT_TOKEN'), parse_mode="HTML")
    
    # �������� ����������
    dp = Dispatcher(storage=MemoryStorage())
    
    # ����������� middleware
    dp.message.middleware(DatabaseMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    # ����������� ���������
    setup_handlers(dp)
    
    # ����������� startup/shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # ������
    try:
        logger.info(" ��� ������� � ����� � ������!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f" ����������� ������: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info(" ��� ���������� �������������")
    except Exception as e:
        logger.error(f" �������������� ������: {e}")
        sys.exit(1)

