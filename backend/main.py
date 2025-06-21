#!/usr/bin/env python3
"""
Главная точка входа для запуска VendBot
"""
import sys
import os
import asyncio
from pathlib import Path

# Проверяем наличие необходимых переменных окружения
required_env_vars = ["BOT_TOKEN", "DATABASE_URL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    print(f" Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
    print(" Создайте файл .env или установите переменные в Railway")
    sys.exit(1)

# Запускаем бота
if __name__ == "__main__":
    try:
        from bot.main import main
        print(" Запускаем VendBot...")
        asyncio.run(main())
    except ImportError as e:
        print(f" Ошибка импорта: {e}")
        print(f" Текущая директория: {os.getcwd()}")
        print(f" PYTHONPATH: {sys.path}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n Остановлено пользователем")
    except Exception as e:
        print(f" Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
