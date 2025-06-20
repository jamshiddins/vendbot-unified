FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend directory
COPY backend/ ./backend/

# Create necessary directories
RUN mkdir -p logs uploads

# Set Python path
ENV PYTHONPATH=/app/backend

# Run the bot
CMD ["python", "backend/main.py"]
