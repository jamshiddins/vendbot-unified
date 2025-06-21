import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# База для моделей
Base = declarative_base()

# Получаем DATABASE_URL
database_url = getattr(settings, 'database_url', None) or getattr(settings, 'DATABASE_URL', None) or os.getenv('DATABASE_URL')

if not database_url:
    logger.error("DATABASE_URL не найден в настройках!")
    raise ValueError("DATABASE_URL не установлен")

# Конвертируем URL для asyncpg
if database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')

# Определяем, используется ли pooler
use_pooler = 'pooler' in database_url or 'pgbouncer' in database_url

# Создаем движок с правильными параметрами
if use_pooler:
    # Для pooler используем NullPool без дополнительных параметров
    engine = create_async_engine(
        database_url,
        echo=settings.debug if hasattr(settings, 'debug') else False,
        pool_pre_ping=True,
        poolclass=NullPool
    )
else:
    # Для прямого подключения используем обычный пул
    engine = create_async_engine(
        database_url,
        echo=settings.debug if hasattr(settings, 'debug') else False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )

# Создаем фабрику сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Инициализация базы данных"""
    try:
        # Импортируем модели чтобы они зарегистрировались
        from db import models
        
        # Создаем таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info(" База данных инициализирована успешно")
    except Exception as e:
        logger.error(f" Ошибка инициализации БД: {e}")
        raise

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии БД"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

# Для обратной совместимости
SessionLocal = async_session_maker
get_session = get_db_session
