# Multi-stage production Dockerfile for Bank Statement Table Extraction & Banking Analytics API
# Base: Official Python 3.11 Slim Image
FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HUB_DISABLE_XET=1 \
    PORT=8000 \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000

WORKDIR /app

# Install system dependencies (build-essential, curl for health check)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and necessary metadata
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY data/ ./data/

# Create a non-root user and assign permissions
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data/models_cache /app/data/raw /app/data/processed && \
    chown -R appuser:appuser /app

USER appuser

# Expose API port
EXPOSE 8000

# Docker healthcheck querying the /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Launch uvicorn production server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
