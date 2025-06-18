import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env
env_path = Path(__file__).parent.parent / 'deploy' / 'production' / '.env'
load_dotenv(env_path)

db_url = os.getenv('DATABASE_URL')

print(" Анализ DATABASE_URL:")
print(f"Длина: {len(db_url)}")
print(f"Первые 50 символов: {db_url[:50]}...")
print(f"Последние 20 символов: ...{db_url[-20:]}")

# Проверяем каждый символ
print("\n Проверка на невидимые символы:")
for i, char in enumerate(db_url):
    if ord(char) < 32 or ord(char) > 126:
        print(f"Позиция {i}: невидимый символ с кодом {ord(char)}")

# Показываем байты вокруг позиции 61 (где ошибка)
print(f"\n Байты вокруг позиции 61:")
bytes_db = db_url.encode('utf-8')
for i in range(max(0, 61-5), min(len(bytes_db), 61+5)):
    print(f"Позиция {i}: {bytes_db[i]:02x} ('{chr(bytes_db[i]) if 32 <= bytes_db[i] <= 126 else '?'}')")
