FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов из backend директории
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего кода backend
COPY backend/ ./backend/

# Переход в рабочую директорию
WORKDIR /app/backend

# Railway использует переменную PORT (но наш бот её не использует)
ENV PYTHONPATH=/app/backend

# Команда запуска
CMD ["python", "run_bot.py"]
