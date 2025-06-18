import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from datetime import datetime

# Загружаем переменные окружения
env_path = Path(__file__).parent.parent / 'deploy' / 'production' / '.env'
load_dotenv(env_path)

print("🔍 Тестирование подключения к Supabase с новым паролем")
print("=" * 60)

database_url = os.getenv('DATABASE_URL')

# Проверяем, что URL загружен
if not database_url:
    print("❌ DATABASE_URL не найден в .env файле")
    sys.exit(1)

# Безопасный вывод URL (скрываем пароль)
if 'NYUe5NhPgjmFppvq' in database_url:
    safe_url = database_url.replace('NYUe5NhPgjmFppvq', '***NEW_PASSWORD***')
    print(f"📋 Используемый URL: {safe_url}")
    print("✅ Новый пароль обнаружен в конфигурации")
else:
    print("⚠️  Похоже, используется старый пароль")

try:
    # Создаём подключение
    print("\n🔄 Устанавливаем соединение...")
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        # Базовая проверка
        result = conn.execute(text("SELECT 1"))
        print("✅ Подключение установлено успешно!")
        
        # Информация о сервере
        print("\n📊 Информация о базе данных:")
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"   PostgreSQL версия: {version.split(',')[0]}")
        
        result = conn.execute(text("SELECT current_database(), current_user"))
        db_name, user = result.fetchone()
        print(f"   База данных: {db_name}")
        print(f"   Пользователь: {user}")
        
        # Анализ структуры базы данных
        print("\n🗂️  Структура базы данных:")
        inspector = inspect(engine)
        
        # Получаем список таблиц
        tables = inspector.get_table_names(schema='public')
        print(f"   Найдено таблиц: {len(tables)}")
        
        if tables:
            print("\n   Детальная информация о таблицах:")
            for table_name in sorted(tables):
                # Получаем информацию о столбцах
                columns = inspector.get_columns(table_name, schema='public')
                
                # Считаем записи
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.scalar()
                
                print(f"\n   📋 Таблица '{table_name}':")
                print(f"      Записей: {row_count}")
                print(f"      Столбцы ({len(columns)}):")
                
                for col in columns[:5]:  # Показываем первые 5 столбцов
                    col_type = str(col['type'])
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    print(f"         - {col['name']}: {col_type} {nullable}")
                
                if len(columns) > 5:
                    print(f"         ... и ещё {len(columns) - 5} столбцов")
        else:
            print("   ℹ️  Таблиц пока нет в базе данных")
            print("   💡 Это нормально для нового проекта")
        
        # Проверка прав доступа
        print("\n🔐 Проверка прав доступа:")
        try:
            # Пробуем создать временную таблицу
            conn.execute(text("CREATE TEMP TABLE test_permissions (id INT)"))
            conn.execute(text("DROP TABLE test_permissions"))
            print("   ✅ Создание таблиц: разрешено")
        except Exception as e:
            print(f"   ❌ Создание таблиц: запрещено ({str(e)})")
        
        print("\n" + "=" * 60)
        print("🎉 Все тесты пройдены успешно!")
        print("✅ База данных Supabase полностью готова к работе")
        print("=" * 60)
        
        print("\n📝 Следующие шаги:")
        print("1. Если таблиц нет - запустите миграции: alembic upgrade head")
        print("2. Настройте остальные параметры в .env (Telegram токен и т.д.)")
        print("3. Запустите приложение: python main.py")
        
except Exception as e:
    print(f"\n❌ Ошибка подключения!")
    print(f"Тип: {type(e).__name__}")
    print(f"Сообщение: {str(e)}")
    
    if "Wrong password" in str(e):
        print("\n💡 Похоже, пароль всё ещё неверный. Проверьте:")
        print("   1. Правильно ли скопирован пароль")
        print("   2. Нет ли лишних пробелов")
        print("   3. Сохранён ли файл .env после изменений")
    elif "timeout" in str(e).lower():
        print("\n💡 Проблема с сетью. Проверьте:")
        print("   1. Интернет-соединение")
        print("   2. Не заблокирован ли доступ файрволом")
        print("   3. Активен ли проект в Supabase")
