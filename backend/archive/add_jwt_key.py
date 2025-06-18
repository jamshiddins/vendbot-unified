import os
import re
import secrets

# Читаем .env файл
env_path = '.env'

with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Генерируем новый JWT_SECRET_KEY
jwt_secret = secrets.token_urlsafe(32)

# Проверяем, есть ли уже JWT_SECRET_KEY
if 'JWT_SECRET_KEY=' in content:
    # Заменяем существующий, если он не настроен
    content = re.sub(
        r'JWT_SECRET_KEY=another-secret-key-for-jwt',
        f'JWT_SECRET_KEY={jwt_secret}',
        content
    )
    print(f" JWT_SECRET_KEY обновлён")
else:
    # Добавляем новый
    if not content.endswith('\n'):
        content += '\n'
    content += f'JWT_SECRET_KEY={jwt_secret}\n'
    print(f" JWT_SECRET_KEY добавлен")

# Сохраняем
with open(env_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f" JWT_SECRET_KEY: {jwt_secret}")
