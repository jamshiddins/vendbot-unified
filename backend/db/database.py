from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from core.config import settings
import asyncio

# Базовый класс для моделей
Base = declarative_base()

# Создаем асинхронный движок с настройками для Supabase
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    poolclass=NullPool,  # Важно для pgbouncer
    pool_pre_ping=True,
    connect_args={
        "server_settings": {
            "application_name": "vendbot"
        },
        "statement_cache_size": 0,  # Отключаем prepared statements
        "command_timeout": 60
    }
)

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Dependency для получения сессии
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
