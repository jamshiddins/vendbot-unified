import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from db.models import Machine, Ingredient
import os
from dotenv import load_dotenv

load_dotenv()

async def add_test_data():
    print("Добавление тестовых данных...")

    engine = create_async_engine(os.getenv("DATABASE_URL"))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Создаем автоматы
        machines = [
            Machine(code="CVM-001", name="Кофемашина 1", location="Офис А", status="active"),
            Machine(code="CVM-002", name="Кофемашина 2", location="Офис Б", status="active"),
            Machine(code="CVM-003", name="Кофемашина 3", location="Склад", status="maintenance"),
        ]
        
        # Создаем ингредиенты
        ingredients = [
            Ingredient(code="COFFEE-001", name="Кофе в зернах", unit="кг", current_stock=50.0),
            Ingredient(code="SUGAR-001", name="Сахар", unit="кг", current_stock=30.0),
            Ingredient(code="MILK-001", name="Молоко", unit="л", current_stock=20.0),
        ]

        session.add_all(machines + ingredients)
        await session.commit()
        print(" Тестовые данные добавлены!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_test_data())
