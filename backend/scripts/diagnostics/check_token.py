import os
import sys
from pathlib import Path

# Добавляем текущую директорию в path
sys.path.insert(0, str(Path.cwd()))

print("=" * 60)
print("🔍 Проверка BOT_TOKEN")
print("=" * 60)

# 1. Проверяем .env файл
if Path('.env').exists():
    print("\n Содержимое .env:")
    with open('.env', 'r') as f:
        for line in f:
            if 'BOT_TOKEN' in line:
                print(f"  {line.strip()}")
else:
    print("\n Файл .env не найден!")

# 2. Проверяем переменную окружения
from dotenv import load_dotenv
load_dotenv()

token_from_env = os.getenv('BOT_TOKEN')
print(f"\n BOT_TOKEN из окружения: {token_from_env[:20]}..." if token_from_env and len(token_from_env) > 20 else "NOT SET")

# 3. Проверяем конфигурацию
try:
    from core.config import get_settings
    settings = get_settings()
    token_from_config = settings.BOT_TOKEN
    print(f" BOT_TOKEN из конфига: {token_from_config[:20]}..." if token_from_config and len(token_from_config) > 20 else "NOT SET")
except Exception as e:
    print(f" Ошибка загрузки конфига: {e}")

print("\n" + "=" * 60)
