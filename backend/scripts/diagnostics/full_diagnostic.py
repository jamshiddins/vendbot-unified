import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import subprocess

print("🔍 Комплексная диагностика проекта VendBot")
print("=" * 70)

# Загружаем .env
env_path = Path(__file__).parent.parent / 'deploy' / 'production' / '.env'
load_dotenv(env_path)

# 1. Проверка переменных окружения
print("\n 1. ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ")
print("-" * 50)

env_vars = {
    "DATABASE_URL": {
        "value": os.getenv("DATABASE_URL"),
        "check": lambda v: v and "postgresql://" in v,
        "description": "Подключение к базе данных"
    },
    "BOT_TOKEN": {
        "value": os.getenv("BOT_TOKEN"),
        "check": lambda v: v and v != "your_bot_token_from_botfather",
        "description": "Токен Telegram бота"
    },
    "SECRET_KEY": {
        "value": os.getenv("SECRET_KEY"),
        "check": lambda v: v and v != "your-secret-key-here-generate-a-random-one",
        "description": "Секретный ключ приложения"
    },
    "JWT_SECRET_KEY": {
        "value": os.getenv("JWT_SECRET_KEY"),
        "check": lambda v: v and v != "another-secret-key-for-jwt",
        "description": "Секретный ключ для JWT"
    },
    "REDIS_URL": {
        "value": os.getenv("REDIS_URL"),
        "check": lambda v: v is not None,
        "description": "Подключение к Redis"
    }
}

all_env_ok = True
for key, info in env_vars.items():
    if info["check"](info["value"]):
        print(f" {key}: {info['description']}")
    else:
        print(f" {key}: {info['description']} - ТРЕБУЕТ НАСТРОЙКИ")
        all_env_ok = False

# 2. Проверка Python модулей
print("\n\n 2. PYTHON МОДУЛИ")
print("-" * 50)

modules = {
    "psycopg2": "PostgreSQL драйвер",
    "sqlalchemy": "ORM",
    "alembic": "Миграции БД",
    "aiogram": "Telegram Bot API",
    "fastapi": "Web API",
    "uvicorn": "ASGI сервер",
    "redis": "Redis клиент",
    "pydantic": "Валидация данных"
}

all_modules_ok = True
for module, description in modules.items():
    try:
        __import__(module)
        print(f" {module}: {description}")
    except ImportError:
        print(f" {module}: {description} - НЕ УСТАНОВЛЕН")
        all_modules_ok = False

# 3. Проверка структуры файлов
print("\n\n 3. СТРУКТУРА ПРОЕКТА")
print("-" * 50)

files_to_check = [
    ("main.py", "Главный файл"),
    ("alembic.ini", "Конфигурация миграций"),
    ("requirements.txt", "Зависимости"),
    ("core/config.py", "Конфигурация"),
    ("db/models/base.py", "Базовая модель"),
    ("bot/main.py", "Telegram бот"),
    ("api/main.py", "FastAPI приложение")
]

all_files_ok = True
for file_path, description in files_to_check:
    if Path(file_path).exists():
        print(f" {file_path}: {description}")
    else:
        print(f" {file_path}: {description} - НЕ НАЙДЕН")
        all_files_ok = False

# 4. Проверка базы данных
print("\n\n 4. БАЗА ДАННЫХ")
print("-" * 50)

try:
    import psycopg2
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Проверяем версию
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f" PostgreSQL подключен: {version.split(',')[0]}")
        
        # Проверяем таблицы
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        if tables:
            print(f" Найдено таблиц: {len(tables)}")
            for table in tables[:5]:
                print(f"   - {table}")
            if len(tables) > 5:
                print(f"   ... и ещё {len(tables) - 5}")
        else:
            print("  Таблиц нет (нужно запустить миграции)")
        
        cursor.close()
        conn.close()
        db_ok = True
    else:
        print(" DATABASE_URL не настроен")
        db_ok = False
except Exception as e:
    print(f" Ошибка подключения к БД: {str(e)[:50]}...")
    db_ok = False

# 5. Проверка миграций Alembic
print("\n\n 5. МИГРАЦИИ ALEMBIC")
print("-" * 50)

try:
    # Проверяем текущую версию
    result = subprocess.run(
        ["alembic", "current"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(" Alembic настроен")
        if result.stdout.strip():
            print(f"   Текущая версия: {result.stdout.strip()}")
        else:
            print("    Миграции не применены")
    else:
        print(" Ошибка Alembic:", result.stderr[:100])
    alembic_ok = result.returncode == 0
except Exception as e:
    print(f" Alembic не найден: {e}")
    alembic_ok = False

# Итоговый отчёт
print("\n\n" + "=" * 70)
print(" ИТОГОВЫЙ ОТЧЁТ")
print("=" * 70)

checks = {
    "Переменные окружения": all_env_ok,
    "Python модули": all_modules_ok,
    "Структура проекта": all_files_ok,
    "База данных": db_ok,
    "Alembic": alembic_ok
}

all_ok = all(checks.values())

for check, status in checks.items():
    print(f"{check}: {' OK' if status else ' Требует внимания'}")

print("\n" + "=" * 70)

if all_ok:
    print(" Проект полностью готов к запуску!")
    print("\nКоманды для запуска:")
    print("1. alembic upgrade head  # Применить миграции")
    print("2. python main.py        # Запустить приложение")
else:
    print("  Некоторые компоненты требуют настройки")
    print("\nРекомендации:")
    if not all_env_ok:
        print("- Настройте недостающие переменные в файле .env")
    if not all_modules_ok:
        print("- Установите модули: pip install -r requirements.txt")
    if not all_files_ok:
        print("- Проверьте структуру проекта")
    if not db_ok:
        print("- Проверьте подключение к базе данных")
    if not alembic_ok:
        print("- Настройте Alembic для миграций")

# Генерация секретных ключей
if not all_env_ok:
    print("\n Совет: Для генерации секретных ключей используйте:")
    print("python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
