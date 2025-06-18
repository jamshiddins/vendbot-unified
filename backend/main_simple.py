import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.config import settings
from bot.main import BotManager
from api.websocket import ws_manager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Менеджер бота
bot_manager = BotManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info(f" Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Запускаем бота если включен
    if settings.ENABLE_BOT:
        await bot_manager.start()
        logger.info(" Telegram bot started")
    
    yield
    
    # Shutdown
    logger.info(" Shutting down...")
    if settings.ENABLE_BOT:
        await bot_manager.stop()
    logger.info(" Application stopped")

# Создаем приложение
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Простой эндпоинт для проверки
@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info(f" Starting {settings.APP_NAME}...")
    
    # Запускаем FastAPI и бота одновременно
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
