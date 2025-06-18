import asyncio
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.ext.asyncio import create_async_engine
from db.models.base import Base
from db.models import *  # Импортируем все модели
from core.config import settings

# Используем синхронный движок для DDL операций
sync_url = settings.DATABASE_URL.replace("+asyncpg", "")
engine = create_engine(sync_url)

print(" Пересоздание таблиц в базе данных...\n")

try:
    # Удаляем существующие таблицы
    print(" Удаление существующих таблиц...")
    meta = MetaData()
    meta.reflect(bind=engine)
    
    # Удаляем таблицы в обратном порядке зависимостей
    tables_to_drop = ['hopper_operations', 'assets', 'ingredients', 'users']
    
    with engine.begin() as conn:
        for table_name in tables_to_drop:
            if table_name in meta.tables:
                print(f"  - Удаление таблицы {table_name}")
                conn.execute(text(f'DROP TABLE IF EXISTS {table_name} CASCADE'))
        
        # Удаляем ENUM типы если есть
        print("\n Удаление ENUM типов...")
        conn.execute(text("DROP TYPE IF EXISTS assettype CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS operationtype CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS userrole CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS hopper_status CASCADE"))
        
    print("\n Старые таблицы удалены")
    
    # Создаем новые таблицы
    print("\n Создание новых таблиц...")
    Base.metadata.create_all(bind=engine)
    
    # Проверяем созданные таблицы
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name NOT LIKE 'pg_%'
            ORDER BY table_name
        """))
        
        print("\n Созданные таблицы:")
        for row in result:
            print(f"  - {row[0]}")
            
    # Обновляем alembic_version
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM alembic_version"))
        conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('4d4fd9217dc0')"))
        print("\n Версия миграции обновлена")
        
except Exception as e:
    print(f"\n Ошибка: {e}")
    import traceback
    traceback.print_exc()
finally:
    engine.dispose()

print("\n База данных готова к работе!")
