import os
from typing import List, Union, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    # Bot settings - используем Field для алиасов
    bot_token: str = Field(alias="BOT_TOKEN")
    admin_ids: Union[str, List[int]] = Field(default=[], alias="ADMIN_IDS")
    
    # Database settings - поддерживаем оба варианта
    database_url: str = Field(alias="DATABASE_URL")
    
    # Security settings
    secret_key: str = Field(default="change-in-production", alias="SECRET_KEY")
    jwt_secret_key: str = Field(default="change-in-production", alias="JWT_SECRET_KEY")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    
    # Application settings
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="production", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # API settings
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    
    # App info
    app_name: str = Field(default="VendBot", alias="APP_NAME")
    app_version: str = Field(default="2.0.0", alias="APP_VERSION")
    
    @validator("admin_ids", pre=True)
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        elif isinstance(v, int):
            return [v]
        elif isinstance(v, list):
            return v
        return []
    
    # Добавляем свойство для обратной совместимости
    @property
    def DATABASE_URL(self):
        return self.database_url
    
    @property
    def BOT_TOKEN(self):
        return self.bot_token
    
    @property
    def JWT_SECRET_KEY(self):
        return self.jwt_secret_key
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        populate_by_name = True  # Разрешаем использовать имена полей

settings = Settings()
