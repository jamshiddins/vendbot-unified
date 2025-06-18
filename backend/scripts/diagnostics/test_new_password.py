import psycopg2
import sys

# ВАЖНО: Замените NEW_PASSWORD_HERE на ваш новый пароль из Supabase
new_password = "dChAsidTaUPOVyGx"  # <-- Вставьте сюда новый пароль
project_ref = "tyazplmrraxibyeqhach"

print("🔍 Тестирование нового пароля Supabase")
print("=" * 50)
print(f"Проект: {project_ref}")
print(f"Пароль: {new_password[:3]}...{new_password[-3:]}")
print(f"Длина пароля: {len(new_password)}")

# Формируем connection string
connection_string = f"postgresql://postgres.{project_ref}:{new_password}@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"

try:
    print("\n Подключаемся к базе данных...")
    conn = psycopg2.connect(connection_string, connect_timeout=10)
    
    print(" УСПЕХ! Подключение установлено с новым паролем!")
    
    # Проверяем, что подключение рабочее
    cursor = conn.cursor()
    cursor.execute("SELECT current_database(), current_user, version()")
    db_name, user, version = cursor.fetchone()
    
    print(f"\n Информация о подключении:")
    print(f"   База данных: {db_name}")
    print(f"   Пользователь: {user}")
    print(f"   PostgreSQL: {version.split(',')[0]}")
    
    # Проверяем таблицы
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    table_count = cursor.fetchone()[0]
    print(f"   Таблиц в базе: {table_count}")
    
    cursor.close()
    conn.close()
    
    print("\n Новый пароль работает! Теперь обновите файл .env")
    print(f"\nИспользуйте эту строку в .env:")
    print(f"DATABASE_URL={connection_string}")
    
except psycopg2.OperationalError as e:
    print(f"\n Ошибка подключения: {e}")
    if "Wrong password" in str(e):
        print("\n Пароль всё ещё неверный. Убедитесь, что:")
        print("   1. Вы скопировали ВЕСЬ пароль из Supabase")
        print("   2. Нет лишних пробелов в начале или конце")
        print("   3. Вы используете последний сброшенный пароль")
