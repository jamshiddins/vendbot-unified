FROM python:3.11-slim

# Системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем requirements
COPY backend/requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY backend/ ./backend/

# Переменные окружения
ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

# Переходим в backend для запуска
WORKDIR /app/backend

# Проверка структуры (для отладки)
RUN echo "📁 Проверка структуры:" && \
    ls -la && \
    echo "📁 Содержимое bot/:" && \
    ls -la bot/

# Запуск бота
CMD ["python", "main.py"]
