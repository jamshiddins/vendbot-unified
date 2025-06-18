from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import settings

# Создаем базовый класс для моделей
Base = declarative_base()

# Отладка - посмотрим какой URL используется
print(f"[DATABASE] Connecting to: {settings.database_url[:50]}...")

# Создаем движок БД с параметрами для Supabase pgbouncer
engine = create_async_engine(
    settings.database_url,
    echo=True,  # Включаем логирование SQL
    pool_pre_ping=True,
    # ВАЖНО: Отключаем prepared statements для pgbouncer
    connect_args={
        "server_settings": {
            "application_name": "vendbot",
            "jit": "off"
        },
        "command_timeout": 60,
        "ssl": "require",
        # Отключаем кэш prepared statements
        "statement_cache_size": 0,
    }
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
