import asyncio
from aiogram import Bot
from aiogram.exceptions import TelegramUnauthorizedError

async def test_token():
    print('Введите ваш токен бота (формат: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11):')
    token = input().strip()
    
    if not token:
        print(' Токен не введен!')
        return
        
    if ':' not in token:
        print(' Неверный формат токена! Должен содержать ":"')
        return
    
    print(f'\n Проверяем токен: {token[:10]}...{token[-10:]}')
    
    try:
        bot = Bot(token=token)
        bot_info = await bot.get_me()
        await bot.session.close()
        
        print(f' УСПЕХ! Токен рабочий!')
        print(f' Бот: @{bot_info.username}')
        print(f' ID: {bot_info.id}')
        print(f' Имя: {bot_info.first_name}')
        
        # Сохраним рабочий токен
        print('\n Сохранить этот токен в .env? (y/n):')
        if input().lower() == 'y':
            with open('.env', 'r') as f:
                lines = f.readlines()
            
            with open('.env', 'w') as f:
                for line in lines:
                    if line.startswith('BOT_TOKEN='):
                        f.write(f'BOT_TOKEN={token}\n')
                    else:
                        f.write(line)
            print(' Токен сохранен в .env!')
            
    except TelegramUnauthorizedError:
        print(' ОШИБКА: Неверный токен (Unauthorized)')
    except Exception as e:
        print(f' ОШИБКА: {type(e).__name__}: {e}')

if __name__ == '__main__':
    asyncio.run(test_token())
