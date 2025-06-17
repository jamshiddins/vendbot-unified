from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "VendBot"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    SECRET_KEY: str
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Telegram
    BOT_TOKEN: str
    WEBHOOK_URL: str = ""
    ENABLE_BOT: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Storage
    STORAGE_TYPE: str = "local"
    UPLOAD_PATH: str = "./uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Создаем папку для загрузок если не существует
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)