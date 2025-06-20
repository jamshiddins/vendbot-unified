import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import text
from db.database import engine, Base
from db.models import User, Machine, Hopper, Ingredient, HopperOperation
from core.config import settings

async def init_db():
    '''Создание всех таблиц в БД'''
    print('🔨 Создание таблиц в БД...')
    
    try:
        # Создаем все таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print('✅ Таблицы успешно созданы')
        
        # Проверяем созданные таблицы
        async with engine.connect() as conn:
            result = await conn.execute(text('''
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            '''))
            
            tables = result.fetchall()
            print(f'\n📋 Создано таблиц: {len(tables)}')
            for table in tables:
                print(f'   - {table[0]}')
                
    except Exception as e:
        print(f'❌ Ошибка при создании таблиц: {e}')
        raise
    finally:
        await engine.dispose()

if __name__ == '__main__':
    asyncio.run(init_db())
