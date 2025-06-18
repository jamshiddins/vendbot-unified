import sys
import os
from pathlib import Path

print("=== ПРОВЕРКА ОКРУЖЕНИЯ VENDBOT ===\n")

# Проверка Python
print(f"Python версия: {sys.version}")
print(f"Python путь: {sys.executable}\n")

# Проверка структуры проекта
project_root = Path(__file__).parent
print(f"Корень проекта: {project_root}\n")

# Проверка критических файлов
critical_files = [
    ".env",
    "alembic.ini",
    "requirements.txt",
    "pyproject.toml"
]

print("Проверка файлов:")
for file in critical_files:
    path = project_root / file
    status = "" if path.exists() else ""
    print(f"{status} {file}")

# Проверка папок
print("\nПроверка структуры папок:")
folders = [
    "api",
    "bot", 
    "core",
    "db",
    "alembic"
]

for folder in folders:
    path = project_root / folder
    status = "" if path.is_dir() else ""
    print(f"{status} {folder}/")

# Проверка .env
env_path = project_root / ".env"
if env_path.exists():
    print("\n Переменные окружения:")
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key = line.split("=")[0]
                print(f"  - {key}")
else:
    print("\n Файл .env не найден!")
