import os
from typing import List
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

class Settings(BaseSettings):
    # Bot settings
    bot_token: str
    admin_ids: List[int] = []
    
    # Database settings
    database_url: str
    
    # JWT settings
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    
    # Application settings
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Get settings
settings = Settings()

# Create async engine with Supabase-compatible settings
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    connect_args={
        "server_settings": {
            "application_name": "vendbot"
        },
        "statement_cache_size": 0,  # Отключаем prepared statements для Supabase
        "prepared_statement_cache_size": 0,
        "command_timeout": 60
    }
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False
)

# Base for models
Base = declarative_base()

def get_settings() -> Settings:
    return settings
