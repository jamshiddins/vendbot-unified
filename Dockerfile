FROM python:3.11-slim

# Set working directory
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
COPY backend/ ./

# Create necessary directories
RUN mkdir -p logs data uploads

# Set Python path
ENV PYTHONPATH=/app

# Run the bot from backend directory
CMD ["python", "main.py"]
