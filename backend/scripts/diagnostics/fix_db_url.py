import os
import urllib.parse
from dotenv import load_dotenv

# Загружаем .env
load_dotenv('.env')

# Получаем DATABASE_URL
db_url = os.getenv('DATABASE_URL')

print(" Анализ DATABASE_URL...")
print(f"Длина URL: {len(db_url)} символов")

# Проверяем на проблемные символы
if '@' in db_url and '://' in db_url:
    # Разбираем URL безопасно
    try:
        # Находим позиции ключевых элементов
        protocol_end = db_url.find('://')
        at_sign = db_url.rfind('@')
        
        # Извлекаем части
        protocol = db_url[:protocol_end]
        credentials = db_url[protocol_end+3:at_sign]
        host_and_db = db_url[at_sign+1:]
        
        print(f"\nЧасти URL:")
        print(f"  Протокол: {protocol}")
        print(f"  Учетные данные: {len(credentials)} символов")
        print(f"  Хост и БД: {host_and_db}")
        
        # Проверяем пароль
        if ':' in credentials:
            username, password = credentials.split(':', 1)
            print(f"\n  Пользователь: {username}")
            print(f"  Пароль: {len(password)} символов")
            
            # Проверяем нужно ли кодирование
            needs_encoding = False
            for char in password:
                if not (char.isalnum() or char in '-._~'):
                    needs_encoding = True
                    break
            
            if needs_encoding:
                print("\n Пароль содержит специальные символы, требуется URL-кодирование")
                encoded_password = urllib.parse.quote(password, safe='')
                new_url = f"{protocol}://{username}:{encoded_password}@{host_and_db}"
                
                # Обновляем .env
                with open('.env', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                import re
                content = re.sub(
                    r'DATABASE_URL=.*',
                    f'DATABASE_URL={new_url}',
                    content,
                    flags=re.MULTILINE
                )
                
                with open('.env', 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(" DATABASE_URL обновлен с URL-кодированным паролем")
            else:
                print(" Пароль не требует URL-кодирования")
                
    except Exception as e:
        print(f" Ошибка при разборе URL: {e}")
else:
    print(" Неверный формат DATABASE_URL")
