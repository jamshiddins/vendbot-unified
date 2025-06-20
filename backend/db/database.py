from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from core.config import settings, Base
import asyncio
from contextlib import asynccontextmanager

# Для Supabase pgbouncer нужна специальная конфигурация
# Отключаем все виды кэширования prepared statements
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    poolclass=NullPool,  # Обязательно для pgbouncer
    pool_pre_ping=True,
    pool_recycle=300,  # Переподключаемся каждые 5 минут
    connect_args={
        "server_settings": {
            "application_name": "vendbot",
            "jit": "off"
        },
        # Эти настройки критичны для pgbouncer
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "command_timeout": 60,
        "ssl": "prefer",
        # Отключаем все виды prepared statements
        "prepare_threshold": None
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

# Альтернативный метод создания сессии для скриптов
@asynccontextmanager
async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()
