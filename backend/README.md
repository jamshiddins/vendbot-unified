# VendBot - Telegram Bot для управления вендинговыми автоматами

## Функционал

- 👥 Управление пользователями и ролями (Админ, Склад, Оператор, Водитель)
- 🏭 Управление кофейными автоматами
-  Работа с бункерами (создание, взвешивание, заполнение)
-  Складской учет ингредиентов
-  Статистика и отчеты

## Технологии

- Python 3.11
- aiogram 3.x
- SQLAlchemy (async)
- PostgreSQL
- Redis
- Docker

## Установка и запуск

### Локальная разработка

```bash
# Клонировать репозиторий
git clone https://github.com/jamshiddins/vendbot-unified.git
cd vendbot-unified/backend

# Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Настроить .env файл
cp .env.example .env
# Отредактировать .env

# Запустить бота
python run_bot.py
Docker
bashdocker-compose up -d
Структура проекта
backend/
 bot/            # Telegram bot handlers и логика
 db/             # Модели базы данных
 core/           # Конфигурация
 api/            # FastAPI endpoints
 scripts/        # Вспомогательные скрипты
