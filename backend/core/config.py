import os
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import validator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

class Settings(BaseSettings):
    # Bot settings
    bot_token: str
    admin_ids: Union[str, List[int]] = []
    
    # Database settings  
    database_url: str
    
    # JWT settings
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    
    # Application settings
    log_level: str = "INFO"
    
    # Дополнительные поля из .env (опциональные)
    secret_key: str = ""
    redis_url: str = "redis://localhost:6379/0"
    debug: bool = False
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    frontend_url: str = "http://localhost:3000"
    upload_dir: str = "./uploads"
    max_upload_size: int = 10485760
    supabase_url: str = ""
    supabase_project_id: str = ""
    
    @validator('admin_ids', pre=True)
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            # Преобразуем строку в список int
            return [int(x.strip()) for x in v.split(',') if x.strip()]
        elif isinstance(v, int):
            # Если передано одно число
            return [v]
        elif isinstance(v, list):
            return v
        return []
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Игнорировать лишние поля

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
        "statement_cache_size": 0,  # Критично для Supabase pgbouncer
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
