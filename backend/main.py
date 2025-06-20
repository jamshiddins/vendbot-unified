import asyncio
import sys
from pathlib import Path

# Текущая директория уже в PATH благодаря PYTHONPATH в Docker
from bot.main import main

if __name__ == "__main__":
    asyncio.run(main())
