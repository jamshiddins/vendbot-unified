# backend/core/config.py - ОДИН файл
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Telegram
    BOT_TOKEN: str
    
    # Database  
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # API
    API_PREFIX: str = "/api/v1"
    JWT_SECRET_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings()