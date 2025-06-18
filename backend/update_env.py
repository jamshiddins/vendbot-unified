import os
from pathlib import Path
import re
import secrets

# Путь к .env файлу
env_path = Path(__file__).parent.parent / 'deploy' / 'production' / '.env'

print(f"📁 Обновление файла: {env_path}")

# Читаем текущий файл
with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Генерируем новый SECRET_KEY
new_secret_key = secrets.token_urlsafe(32)

# Обновляем значения
updates = {
    'SECRET_KEY': new_secret_key,
    'REDIS_URL': 'redis://localhost:6379/0'
}

# Функция для обновления или добавления переменной
def update_env_var(content, key, value):
    pattern = f'^{key}=.*$'
    replacement = f'{key}={value}'
    
    if re.search(pattern, content, re.MULTILINE):
        # Заменяем существующую
        old_value = re.search(pattern, content, re.MULTILINE).group()
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        return content, f"обновлено (было: {old_value})"
    else:
        # Добавляем новую в конец файла
        if not content.endswith('\n'):
            content += '\n'
        content += f'{replacement}\n'
        return content, "добавлено"

# Обновляем переменные
for key, value in updates.items():
    # Проверяем текущее значение
    current_match = re.search(f'^{key}=(.*)$', content, re.MULTILINE)
    if current_match:
        current_value = current_match.group(1)
        if current_value in ['your-secret-key-here-generate-a-random-one', '']:
            content, action = update_env_var(content, key, value)
            print(f" {key}: {action}")
        else:
            print(f"ℹ  {key}: уже настроен (текущее значение: {current_value[:10]}...)")
    else:
        content, action = update_env_var(content, key, value)
        print(f" {key}: {action}")

# Сохраняем обновлённый файл
with open(env_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n Файл .env обновлён!")
print(f"\n Новый SECRET_KEY: {new_secret_key}")
print("\n Теперь запустите диагностику для проверки:")
print("   python full_diagnostic.py")
