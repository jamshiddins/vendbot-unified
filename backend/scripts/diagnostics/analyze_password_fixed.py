import os
from pathlib import Path
from dotenv import load_dotenv
import hashlib
import base64

# Загружаем файл .env
env_path = Path(__file__).parent.parent / 'deploy' / 'production' / '.env'
print(f"📁 Проверяем файл: {env_path}")

# Читаем файл построчно для детального анализа
with open(env_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("\n🔍 Анализ строки DATABASE_URL:")
for i, line in enumerate(lines, 1):
    if line.strip().startswith('DATABASE_URL'):
        print(f"\nСтрока {i}: {repr(line)}")
        
        # Проверяем наличие невидимых символов
        if line.endswith('\n'):
            print("   ✓ Строка заканчивается символом новой строки (нормально)")
        if line.endswith('\r\n'):
            print("   ⚠️ Строка имеет Windows-стиль окончания (CR+LF)")
        
        # Извлекаем URL
        if '=' in line:
            key, value = line.split('=', 1)
            value = value.strip()
            
            # Ищем пароль в URL
            if '@' in value and ':' in value:
                # Находим пароль между последним : и @
                start = value.rfind(':', 0, value.find('@'))
                end = value.find('@')
                if start != -1 and end != -1:
                    password = value[start+1:end]
                    
                    print(f"\n🔐 Анализ пароля:")
                    print(f"   Пароль: '{password}'")
                    print(f"   Длина: {len(password)} символов")
                    print(f"   Первые 3 символа: '{password[:3]}...'")
                    print(f"   Последние 3 символа: '...{password[-3:]}'")
                    
                    # Проверка на пробелы и табуляцию (исправлено)
                    has_spaces = ' ' in password
                    has_tabs = '\t' in password
                    print(f"   Содержит пробелы: {'Да' if has_spaces else 'Нет'}")
                    print(f"   Содержит табуляцию: {'Да' if has_tabs else 'Нет'}")
                    
                    # Проверка на другие невидимые символы
                    invisible_chars = []
                    for char in password:
                        if ord(char) < 32 or ord(char) == 127:
                            invisible_chars.append(f"\\x{ord(char):02x}")
                    if invisible_chars:
                        print(f"   ⚠️ Содержит невидимые символы: {', '.join(invisible_chars)}")
                    
                    # Проверка на ожидаемый пароль
                    expected = "NYUe5NhPgjmFppvq"
                    print(f"\n   Ожидаемый пароль: '{expected}'")
                    print(f"   Совпадает с ожидаемым: {'✅ Да' if password == expected else '❌ Нет'}")
                    
                    if password != expected:
                        print(f"\n   🔍 Посимвольное сравнение:")
                        max_len = max(len(password), len(expected))
                        for i in range(max_len):
                            if i < len(password) and i < len(expected):
                                c1, c2 = password[i], expected[i]
                                if c1 != c2:
                                    print(f"      Позиция {i}: '{c1}' (код {ord(c1)}) != '{c2}' (код {ord(c2)})")
                            elif i >= len(password):
                                print(f"      Позиция {i}: отсутствует в найденном пароле")
                            else:
                                print(f"      Позиция {i}: отсутствует в ожидаемом пароле")
                    
                    # MD5 хеш для сравнения
                    print(f"\n   MD5 хеш пароля: {hashlib.md5(password.encode()).hexdigest()}")
                    print(f"   MD5 хеш ожидаемого: {hashlib.md5(expected.encode()).hexdigest()}")
                    
                    # Проверка на типичные ошибки копирования
                    print(f"\n   🔍 Проверка на типичные ошибки:")
                    if password.startswith(' ') or password.endswith(' '):
                        print("      ⚠️ Пароль содержит пробелы в начале или конце!")
                    if password.startswith('"') or password.endswith('"'):
                        print("      ⚠️ Пароль содержит кавычки!")
                    if password != password.strip():
                        print("      ⚠️ Пароль содержит пробельные символы по краям!")

print("\n" + "="*60)

# Теперь проверяем через dotenv
load_dotenv(env_path)
db_url = os.getenv('DATABASE_URL')

if db_url:
    print("\n✅ DATABASE_URL загружен через dotenv")
    # Извлекаем пароль из загруженного URL
    if '@' in db_url and ':' in db_url:
        start = db_url.rfind(':', 0, db_url.find('@'))
        end = db_url.find('@')
        if start != -1 and end != -1:
            loaded_password = db_url[start+1:end]
            print(f"   Пароль из dotenv: '{loaded_password}'")
            print(f"   Длина: {len(loaded_password)}")
            
            # Проверяем, совпадают ли пароли
            if loaded_password == "NYUe5NhPgjmFppvq":
                print("   ✅ Пароль корректно загружен из .env")
            else:
                print("   ❌ Пароль отличается от ожидаемого!")
else:
    print("\n❌ DATABASE_URL не загружается через dotenv")

# Дополнительная информация для отладки
print("\n📊 Дополнительная информация:")
print(f"   Текущая рабочая директория: {os.getcwd()}")
print(f"   Путь к файлу .env: {env_path.absolute()}")
print(f"   Файл .env существует: {env_path.exists()}")
