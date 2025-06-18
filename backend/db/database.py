from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import settings

# Создаем базовый класс для моделей
Base = declarative_base()

# Отладка - посмотрим какой URL используется
print(f"[DATABASE] Connecting to: {settings.database_url[:50]}...")

# Создаем движок БД
engine = create_async_engine(
    settings.database_url,
    echo=True,  # Включаем логирование SQL
    pool_pre_ping=True
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
