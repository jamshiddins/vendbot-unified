import asyncio
import sys
sys.path.insert(0, '/app/backend')

from sqlalchemy import text
from db.database import engine

async def check_tables():
    print("🔍 Проверка таблиц в БД...")
    
    try:
        async with engine.connect() as conn:
            # Получаем список таблиц
            result = await conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"\n Найдено таблиц: {len(tables)}")
                for table in tables:
                    print(f"   {table[0]}")
                    
                # Проверяем количество записей в основных таблицах
                print("\n Количество записей:")
                for table_name in ['users', 'machines', 'hoppers', 'ingredients']:
                    try:
                        count_result = await conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                        count = count_result.scalar()
                        print(f"  - {table_name}: {count} записей")
                    except:
                        pass
            else:
                print("\n Таблицы не найдены! Нужно создать.")
                
    except Exception as e:
        print(f" Ошибка: {e}")
    finally:
        await engine.dispose()

asyncio.run(check_tables())
