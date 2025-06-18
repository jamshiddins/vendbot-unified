import asyncio
import sys
sys.path.insert(0, '/app/backend')

from sqlalchemy import text
from db.database import engine
from db.models import Base

async def init_db():
    print(" Инициализация базы данных...")
    
    try:
        # Создаем таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print(" Таблицы созданы успешно!")
        
        # Проверяем созданные таблицы
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            tables = result.fetchall()
            print(f"\n Созданные таблицы ({len(tables)}):")
            for table in tables:
                print(f"  - {table[0]}")
                
    except Exception as e:
        print(f" Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
