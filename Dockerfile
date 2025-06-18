FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование backend директории
COPY backend ./backend

# Установка зависимостей
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# Установка переменных окружения
ENV PYTHONPATH=/app/backend
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Команда запуска
CMD ["python", "run_bot.py"]
