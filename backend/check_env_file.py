import os
from pathlib import Path
from dotenv import load_dotenv
import re

# Путь к файлу .env
env_path = Path(__file__).parent.parent / 'deploy' / 'production' / '.env'

print("🔍 Проверка файла .env...")
print(f"Путь к файлу: {env_path}")
print(f"Файл существует: {env_path.exists()}")

if env_path.exists():
    # Читаем файл напрямую для анализа
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"\n📄 Анализ файла (всего строк: {len(lines)}):")
    
    # Ищем строку с DATABASE_URL
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('DATABASE_URL'):
            print(f"\nСтрока {i}: найден DATABASE_URL")
            
            # Проверяем формат
            if '=' not in line:
                print("❌ Ошибка: нет знака '=' в строке")
                continue
                
            # Разделяем на ключ и значение
            key, value = line.split('=', 1)
            value = value.strip()
            
            # Скрываем пароль для безопасного вывода
            safe_value = re.sub(r':([^:@]+)@', r':[HIDDEN]@', value)
            print(f"   Ключ: '{key.strip()}'")
            print(f"   Значение: '{safe_value}'")
            
            # Проверки на распространённые проблемы
            if value.startswith('"') or value.startswith("'"):
                print("⚠️  Предупреждение: значение начинается с кавычки")
            if value.endswith('"') or value.endswith("'"):
                print("⚠️  Предупреждение: значение заканчивается кавычкой")
            if ' ' in value:
                print("⚠️  Предупреждение: в значении есть пробелы")
            if '\n' in value or '\r' in value:
                print("⚠️  Предупреждение: в значении есть символы новой строки")
                
            # Извлекаем пароль для проверки
            password_match = re.search(r':([^:@]+)@', value)
            if password_match:
                password = password_match.group(1)
                print(f"\n🔐 Информация о пароле:")
                print(f"   Длина: {len(password)} символов")
                print(f"   Начинается с: {password[:2]}...")
                print(f"   Заканчивается на: ...{password[-2:]}")
                
                # Проверяем известный пароль
                if password == "7VFRINXwBaVx5Lkk":
                    print("   ✅ Пароль соответствует ожидаемому")
                else:
                    print("   ❌ Пароль НЕ соответствует ожидаемому!")
                    print(f"   Ожидалось: 7VFRINXwBaVx5Lkk")
                    print(f"   Найдено: {password}")

# Теперь проверяем через dotenv
print("\n🔄 Проверка загрузки через dotenv...")
load_dotenv(env_path)
db_url = os.getenv('DATABASE_URL')

if db_url:
    safe_url = re.sub(r':([^:@]+)@', r':[HIDDEN]@', db_url)
    print(f"✅ DATABASE_URL загружен через dotenv")
    print(f"   Значение: {safe_url}")
else:
    print("❌ DATABASE_URL не загружается через dotenv")
