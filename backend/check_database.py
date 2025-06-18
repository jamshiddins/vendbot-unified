import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

async def check_db():
    print("=== ПРОВЕРКА ПОДКЛЮЧЕНИЯ К БД ===\n")
    
    db_url = os.getenv("DATABASE_URL")
    print(f"Database URL: {db_url[:30]}...")
    
    try:
        engine = create_async_engine(db_url)
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(" Подключение к БД успешно!")
            
            # Проверяем таблицы
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            result = await conn.execute(tables_query)
            tables = result.fetchall()
            
            print(f"\n Найдено таблиц: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
                
        await engine.dispose()
        
    except Exception as e:
        print(f" Ошибка подключения к БД: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
