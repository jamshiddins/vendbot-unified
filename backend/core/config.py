import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Bot settings
    bot_token: str = os.getenv("BOT_TOKEN", "")
    admin_ids: List[int] = [42283329]
    
    # Database
    database_url: str = ""
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # JWT для API (опционально)
    jwt_secret_key: Optional[str] = os.getenv("JWT_SECRET_KEY", None)
    
    # Other settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    timezone: str = os.getenv("TZ", "Asia/Tashkent")
    
    def __init__(self):
        super().__init__()
        # Обработка DATABASE_URL от Railway
        db_url = os.getenv("DATABASE_URL", "")
        if db_url.startswith("postgresql://"):
            self.database_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        else:
            self.database_url = db_url or "postgresql+asyncpg://postgres:postgres@localhost/vendbot"
            
        # Проверка bot_token
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
    
    class Config:
        case_sensitive = False

settings = Settings()
