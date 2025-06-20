FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with verbose output
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    python -c "import asyncpg; print('asyncpg version:', asyncpg.__version__)"

# Copy backend directory
COPY backend/ ./backend/

# Create necessary directories
RUN mkdir -p logs uploads

# Set environment
ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

# Change to backend directory before running
WORKDIR /app/backend

# Run the bot
CMD ["python", "main.py"]
