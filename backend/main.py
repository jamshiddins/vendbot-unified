#!/usr/bin/env python3
"""
Главная точка входа для запуска VendBot
"""
import sys
import os
from pathlib import Path

# Устанавливаем PYTHONPATH на корень backend
sys.path.insert(0, str(Path(__file__).parent))

# Загружаем переменные окружения из .env если есть
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Проверяем наличие необходимых переменных окружения
required_env_vars = ['BOT_TOKEN', 'DATABASE_URL', 'JWT_SECRET_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
    print("💡 Создайте файл .env или установите переменные в Railway")
    sys.exit(1)

# Запускаем бота
if __name__ == "__main__":
    try:
        from bot.main import main
        import asyncio
        
        print("🚀 Запускаем VendBot...")
        asyncio.run(main())
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print(f"📁 Текущая директория: {os.getcwd()}")
        print(f"📋 PYTHONPATH: {sys.path}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Остановлено пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
