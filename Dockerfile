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

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy all backend code
COPY backend/ ./

# Create necessary directories
RUN mkdir -p logs uploads

# Set environment
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"]
