from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from core.config import settings
import asyncio
from functools import partial

# Создаем базовый класс для моделей
Base = declarative_base()

# Преобразуем URL для psycopg2
db_url = settings.database_url
if "+asyncpg" in db_url:
    db_url = db_url.replace("+asyncpg", "")
elif "postgresql://" in db_url and "+" not in db_url:
    # URL уже в нужном формате
    pass

print(f"[DATABASE] Connecting to: {db_url[:50]}...")

# Создаем СИНХРОННЫЙ движок
sync_engine = create_engine(
    db_url,
    echo=True,
    poolclass=NullPool,  # Важно для pgbouncer
    pool_pre_ping=True
)

# Создаем синхронную фабрику сессий
SyncSessionLocal = sessionmaker(
    sync_engine,
    expire_on_commit=False
)

async def get_session():
    """Получить сессию БД с async обработкой"""
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        await asyncio.get_event_loop().run_in_executor(None, session.close)

# Для обратной совместимости
AsyncSessionLocal = SyncSessionLocal
engine = sync_engine
