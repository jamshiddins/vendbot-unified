import os
from typing import List, Optional

class Settings:
    def __init__(self):
        # Bot settings
        self.bot_token = os.getenv("BOT_TOKEN", "")
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
            
        # Admin IDs
        admin_ids_str = os.getenv("ADMIN_IDS", "42283329")
        self.admin_ids = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
        
        # Database
        db_url = os.getenv("DATABASE_URL", "")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable is required")
            
        # Для Supabase pooler используем psycopg2
        if "pooler.supabase.com" in db_url:
            # Заменяем префикс для использования с psycopg2
            if db_url.startswith("postgresql://"):
                self.database_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
            elif db_url.startswith("postgresql+asyncpg://"):
                self.database_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
            else:
                self.database_url = db_url
        else:
            # Для других БД используем asyncpg
            if db_url.startswith("postgresql://"):
                self.database_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            else:
                self.database_url = db_url
        
        # Redis
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # JWT (опционально)
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", None)
        
        # Other settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.timezone = os.getenv("TZ", "Asia/Tashkent")
        
        print(f"[CONFIG] Using database URL: {self.database_url[:50]}...")

settings = Settings()
