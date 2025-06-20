from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from core.config import settings  # Убрали backend.
import asyncio

# Корректируем DATABASE_URL для asyncpg
database_url = settings.database_url
if "postgresql://" in database_url and "+asyncpg" not in database_url:
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

# Создаем асинхронный движок с настройками для Supabase pgbouncer
engine = create_async_engine(
    database_url,
    echo=False,
    poolclass=NullPool,  # Обязательно для pgbouncer
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "server_settings": {
            "application_name": "vendbot",
            "jit": "off"
        },
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "command_timeout": 60,
        "ssl": "prefer"
    }
)

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Base для моделей
Base = declarative_base()

# Dependency для получения сессии
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
