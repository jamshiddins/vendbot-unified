﻿FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование только директории backend
COPY backend/ ./

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Установка PYTHONPATH
ENV PYTHONPATH=/app

# Команда запуска
CMD ["python", "run_bot.py"]
