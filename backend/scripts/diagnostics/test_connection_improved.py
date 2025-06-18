import os
import sys
from pathlib import Path
import psycopg2
from sqlalchemy import create_engine, text

print(" Проверка актуального состояния подключения (улучшенная версия)")
print("=" * 60)

# Определяем путь к файлу .env более надёжно
# Ищем папку vendbot-unified, начиная от текущей директории
current_path = Path.cwd()
print(f"Текущая директория: {current_path}")

# Ищем файл .env в разных возможных местах
possible_env_paths = [
    current_path / "deploy" / "production" / ".env",
    current_path / "vendbot-unified" / "deploy" / "production" / ".env",
    current_path / ".." / "deploy" / "production" / ".env",
    Path("D:/Projects/vendhub24/vendbot-unified/deploy/production/.env")  # Абсолютный путь как запасной вариант
]

env_path = None
for path in possible_env_paths:
    if path.exists():
        env_path = path
        print(f" Найден файл .env: {env_path}")
        break

if not env_path:
    print(" Файл .env не найден ни в одном из ожидаемых мест!")
    print("Проверенные пути:")
    for path in possible_env_paths:
        print(f"  - {path}")
    sys.exit(1)

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv(env_path)
database_url = os.getenv('DATABASE_URL')

if not database_url:
    print(" DATABASE_URL не найден в файле .env!")
    print(f"Содержимое файла {env_path}:")
    with open(env_path, 'r') as f:
        for line in f:
            if 'DATABASE' in line:
                print(f"  {line.strip()}")
    sys.exit(1)

print(f" DATABASE_URL загружен успешно")

# Безопасный вывод URL
safe_url = database_url.replace('dChAsidTaUPOVyGx', '***PASSWORD***')
print(f"URL: {safe_url}")

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
    print(f" Ошибка: {str(e)}")

# Тест 2: Подключение через SQLAlchemy
print("\n Тест 2: Подключение через SQLAlchemy")
try:
    engine = create_engine(database_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        print(f" Успешно! Результат: {result}")
except Exception as e:
    print(f" Ошибка: {str(e)}")

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
    print("Можете переходить к следующим этапам настройки проекта.")
elif success_count > 0:
    print("\n Подключение работает нестабильно")
    print("Это может быть связано с сетевыми задержками или ограничениями connection pool.")
else:
    print("\n Подключение не работает")
    print("Проверьте правильность пароля и настроек в файле .env")
