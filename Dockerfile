FROM python:3.11-alpine

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    python3-dev

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/

# Create directories
RUN mkdir -p logs uploads

ENV PYTHONPATH=/app/backend
CMD ["python", "backend/main.py"]
