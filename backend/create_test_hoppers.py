import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from db.models import Hopper, HopperStatus
import os
from dotenv import load_dotenv

load_dotenv()

async def create_test_hoppers():
    engine = create_async_engine(os.getenv("DATABASE_URL"))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Создаем несколько тестовых бункеров
        hoppers = [
            Hopper(number="H001", status=HopperStatus.EMPTY, weight_empty=2.5, weight_with_lid=2.7),
            Hopper(number="H002", status=HopperStatus.EMPTY, weight_empty=2.4, weight_with_lid=2.6),
            Hopper(number="H003", status=HopperStatus.EMPTY, weight_empty=2.6, weight_with_lid=2.8),
        ]
        
        session.add_all(hoppers)
        await session.commit()
        print(" Тестовые бункеры созданы")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_test_hoppers())
