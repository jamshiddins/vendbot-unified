import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine, text

# Загружаем .env
env_path = Path(__file__).parent.parent / 'deploy' / 'production' / '.env'
load_dotenv(env_path)
database_url = os.getenv('DATABASE_URL')

print(" Проверка актуального состояния подключения")
print("=" * 60)

# Извлекаем пароль из URL для проверки
if database_url and '@' in database_url and ':' in database_url:
    start = database_url.rfind(':', 0, database_url.find('@'))
    end = database_url.find('@')
    if start != -1 and end != -1:
        current_password = database_url[start+1:end]
        print(f"Текущий пароль в .env: {current_password[:3]}...{current_password[-3:]}")
        print(f"Ожидаемый пароль: dCh...yGx")
        print(f"Пароли совпадают: {' Да' if current_password == 'dChAsidTaUPOVyGx' else ' Нет'}")

# Тест 1: Прямое подключение через psycopg2
print("\n Тест 1: Прямое подключение через psycopg2")
try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()[0]
    print(f" Успешно! Результат: {result}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f" Ошибка: {str(e)[:100]}...")

# Тест 2: Подключение через SQLAlchemy
print("\n Тест 2: Подключение через SQLAlchemy")
try:
    engine = create_engine(database_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        print(f" Успешно! Результат: {result}")
except Exception as e:
    print(f" Ошибка: {str(e)[:100]}...")

# Тест 3: Множественные подключения
print("\n Тест 3: Проверка стабильности (5 подключений подряд)")
success_count = 0
for i in range(5):
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        success_count += 1
        print(f"   Попытка {i+1}: ")
    except Exception as e:
        print(f"   Попытка {i+1}:  - {str(e)[:50]}...")

print(f"\nУспешных подключений: {success_count}/5")

if success_count == 5:
    print("\n Подключение стабильно работает!")
elif success_count > 0:
    print("\n Подключение работает нестабильно")
else:
    print("\n Подключение не работает")
