import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from core.config import settings
from api.routes import api_router
from bot.main import bot_manager
from db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    print("🚀 Starting VendBot...")
    await init_db()
    if settings.ENABLE_BOT:
        await bot_manager.start()
    print("✅ VendBot started successfully!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down VendBot...")
    if settings.ENABLE_BOT:
        await bot_manager.stop()
    print("👋 VendBot stopped.")

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

# 📁 Монтируем статические файлы
app.mount(
    "/photos",
    StaticFiles(directory=settings.UPLOAD_PATH / "photos"),
    name="photos"
)

# 📦 Подключаем маршруты
app.include_router(api_router, prefix="/api/v2")

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )