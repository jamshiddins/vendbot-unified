"""
VendBot Unified Backend
Версия: 2.0.0
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logging import setup_logging
from db.database import init_db
from api.routes import api_router
from bot.main import bot_manager

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info(" Запуск VendBot Backend...")
    
    # Инициализация БД
    await init_db()
    logger.info(" База данных инициализирована")
    
    # Запуск Telegram бота
    asyncio.create_task(bot_manager.start())
    logger.info(" Telegram бот запущен")
    
    yield
    
    # Остановка при завершении
    logger.info(" Остановка VendBot Backend...")
    await bot_manager.stop()

# Создание FastAPI приложения
app = FastAPI(
    title="VendBot API",
    version="2.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {
        "name": "VendBot Backend",
        "version": "2.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "bot": "operational",
            "database": "operational"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
