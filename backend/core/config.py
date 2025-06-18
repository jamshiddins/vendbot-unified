import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Bot settings
    bot_token: str = ""
    admin_ids: List[int] = []
    
    # Database
    database_url: str = ""
    
    # Redis
    redis_url: str = ""
    
    # JWT для API (опционально)
    jwt_secret_key: Optional[str] = None
    
    # Other settings
    log_level: str = "INFO"
    timezone: str = "Asia/Tashkent"
    
    def __init__(self):
        # Сначала заполняем значения из переменных окружения
        self.bot_token = os.getenv("BOT_TOKEN", "")
        
        # Парсим ADMIN_IDS - может быть число или список через запятую
        admin_ids_str = os.getenv("ADMIN_IDS", "42283329")
        if admin_ids_str:
            # Разбиваем по запятой и конвертируем в int
            self.admin_ids = [int(id.strip()) for id in admin_ids_str.split(",")]
        else:
            self.admin_ids = [42283329]  # По умолчанию
            
        # Redis URL
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # JWT (опционально)
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", None)
        
        # Другие настройки
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.timezone = os.getenv("TZ", "Asia/Tashkent")
        
        # Обработка DATABASE_URL от Railway
        db_url = os.getenv("DATABASE_URL", "")
        if db_url.startswith("postgresql://"):
            self.database_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        else:
            self.database_url = db_url or "postgresql+asyncpg://postgres:postgres@localhost/vendbot"
            
        # Проверка bot_token
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        # Вызываем родительский init БЕЗ валидации
        super().__init__(_env_file=None)
    
    class Config:
        validate_assignment = False
        arbitrary_types_allowed = True

settings = Settings()
