# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better cache usage
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a non-root user
RUN useradd -m nonroot && \
    chown -R nonroot:nonroot /app
USER nonroot

# Use gunicorn with gevent worker
CMD exec gunicorn --bind :$PORT \
    --workers 2 \
    --threads 8 \
    --worker-class gevent \
    --worker-connections 1000 \
    --keep-alive 75 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --timeout 0 \
    app:app
