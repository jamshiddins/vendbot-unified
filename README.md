# VendBot Unified

Универсальная система управления вендинговой сетью с поддержкой Telegram, Web и Mobile интерфейсов.

## 🚀 Быстрый старт

### Требования
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Локальная разработка
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env

# Frontend
cd frontend/dashboard
npm install
npm start