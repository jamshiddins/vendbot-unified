FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка зависимостей
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего проекта
COPY . .

# Установка PYTHONPATH для правильного импорта модулей
ENV PYTHONPATH=/app/backend

# Рабочая директория остается /app
WORKDIR /app

# Команда запуска из корня
CMD ["python", "backend/run_bot.py"]
