import os
import psycopg2
from urllib.parse import urlparse

# Ваши данные проекта
project_ref = "tyazplmrraxibyeqhach"
password = "7VFRINXwBaVx5Lkk"

# Различные варианты подключения к Supabase
connection_variants = {
    "Pooler (порт 5432)": f"postgresql://postgres.{project_ref}:{password}@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres",
    "Pooler (порт 6543)": f"postgresql://postgres.{project_ref}:{password}@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres",
    "Direct (порт 5432)": f"postgresql://postgres:{password}@db.{project_ref}.supabase.co:5432/postgres",
}

print("🔍 Тестирование различных вариантов подключения к Supabase\n")

for name, connection_string in connection_variants.items():
    print(f"Тестируем: {name}")
    # Скрываем пароль для вывода
    safe_string = connection_string.replace(password, "***")
    print(f"URL: {safe_string}")
    
    try:
        # Пытаемся подключиться напрямую через psycopg2
        conn = psycopg2.connect(connection_string, connect_timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ Успешно! PostgreSQL версия: {version.split(',')[0]}")
        cursor.close()
        conn.close()
        
        # Если успешно, сохраняем рабочий вариант
        print(f"\n🎉 Используйте этот DATABASE_URL в вашем .env файле:")
        print(f"DATABASE_URL={connection_string}")
        break
        
    except Exception as e:
        error_msg = str(e)
        if "Wrong password" in error_msg:
            print(f"❌ Неверный пароль")
        elif "timeout" in error_msg:
            print(f"❌ Таймаут подключения")
        else:
            print(f"❌ Ошибка: {error_msg}")
        
    print("-" * 60)
    
print("\n📝 Дополнительная диагностика:")
print(f"Project Reference: {project_ref}")
print(f"Длина пароля: {len(password)}")
print("Если все варианты не работают, проверьте:")
print("1. Актуальность пароля в Supabase Dashboard")
print("2. Статус проекта (не приостановлен ли)")
print("3. Правильность региона (ap-southeast-1)")
