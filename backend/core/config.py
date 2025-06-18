import os
from typing import List, Optional

class Settings:
    def __init__(self):
        # Bot settings
        self.bot_token = os.getenv("BOT_TOKEN", "")
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
            
        # Admin IDs - парсим из строки
        admin_ids_str = os.getenv("ADMIN_IDS", "42283329")
        self.admin_ids = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
        
        # Database - ВАЖНОЕ ИЗМЕНЕНИЕ
        db_url = os.getenv("DATABASE_URL", "")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable is required")
            
        # Преобразуем URL для asyncpg
        if db_url.startswith("postgresql://"):
            self.database_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql+asyncpg://"):
            self.database_url = db_url
        else:
            # Если URL уже в другом формате, используем как есть
            self.database_url = db_url
        
        # Redis
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # JWT (опционально)
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", None)
        
        # Other settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.timezone = os.getenv("TZ", "Asia/Tashkent")
        
        # Отладка
        print(f"[CONFIG] Final database_url: {self.database_url[:50]}...")

settings = Settings()
