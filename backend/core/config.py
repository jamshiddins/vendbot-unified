from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/vendbot"
    
    # Bot
    bot_token: str
    webhook_url: Optional[str] = None
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # API
    api_prefix: str = "/api/v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # App settings
    debug: bool = True
    environment: str = "development"
    log_level: str = "INFO"
    
    # Frontend
    frontend_url: str = "http://localhost:3000"
    
    # Upload
    upload_dir: str = "./uploads"
    max_upload_size: int = 10485760
    
    # Additional fields (optional)
    secret_key: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_project_id: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Разрешаем дополнительные поля

settings = Settings()
