from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import settings

# Создаем базовый класс для моделей
Base = declarative_base()

# Создаем движок БД
engine = create_async_engine(
    settings.database_url,  # Исправлено с DATABASE_URL на database_url
    echo=False
)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

async def get_session():
    """Получить сессию БД"""
    async with AsyncSessionLocal() as session:
        yield session
