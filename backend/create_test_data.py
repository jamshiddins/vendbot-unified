import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from db.models import User, UserRole, Machine, Ingredient, Hopper, HopperStatus
import os
from dotenv import load_dotenv

load_dotenv()

async def create_test_data():
    print("Создание тестовых данных...")
    
    engine = create_async_engine(os.getenv("DATABASE_URL"))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Создаем пользователей
        admin = User(
            telegram_id=123456789,
            username="admin",
            full_name="Администратор",
            role=UserRole.ADMIN
        )
        warehouse = User(
            telegram_id=987654321,
            username="warehouse",
            full_name="Кладовщик",
            role=UserRole.WAREHOUSE
        )
        operator = User(
            telegram_id=555555555,
            username="operator",
            full_name="Оператор",
            role=UserRole.OPERATOR
        )
        
        session.add_all([admin, warehouse, operator])
        
        # Создаем автоматы
        for i in range(1, 4):
            machine = Machine(
                code=f"CVM-{i:03d}",
                name=f"Кофемашина {i}",
                location=f"Локация {i}",
                status="active"
            )
            session.add(machine)
        
        # Создаем ингредиенты
        coffee = Ingredient(
            code="COFFEE-001",
            name="Кофе в зернах",
            unit="кг",
            current_stock=50.0
        )
        sugar = Ingredient(
            code="SUGAR-001",
            name="Сахар",
            unit="кг",
            current_stock=30.0
        )
        
        session.add_all([coffee, sugar])
        
        await session.commit()
        print(" Тестовые данные созданы!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_test_data())
