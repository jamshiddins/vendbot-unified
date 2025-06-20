FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including PostgreSQL client
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir asyncpg==0.29.0 && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend directory
COPY backend/ ./backend/

# Create necessary directories
RUN mkdir -p logs uploads

# Set Python path
ENV PYTHONPATH=/app/backend

# Run the bot
CMD ["python", "backend/main.py"]
