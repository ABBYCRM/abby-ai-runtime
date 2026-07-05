# ABBY - Autonomous Business Bot Yielder
# Production Dockerfile for Render Deployment

FROM python:3.11-slim

LABEL maintainer="ABBY Systems"
LABEL version="1.0.0"
LABEL description="Multi-agent AI runtime: MetaGPT + CrewAI"

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for file watcher (if using daemon mode)
RUN mkdir -p /app/watch_folder/incoming /app/watch_folder/completed

# Expose port (Render sets PORT env var)
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-9000}/health || exit 1

# Run the application
CMD ["python", "main.py"]
