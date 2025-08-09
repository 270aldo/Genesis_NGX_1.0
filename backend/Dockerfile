# Multi-stage Dockerfile for NGX Agents API with security best practices
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Set environment variables for build
ENV PYTHONFAULTHANDLER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies needed for building
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Install Google Cloud SDK for Vertex AI
RUN pip install --no-cache-dir --user google-cloud-aiplatform

# Final stage
FROM python:3.11-slim

# Create non-root user with specific UID/GID
RUN groupadd -g 1000 genesis && \
    useradd -r -u 1000 -g genesis -m -d /home/genesis -s /bin/bash genesis

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder --chown=genesis:genesis /root/.local /home/genesis/.local

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PATH=/home/genesis/.local/bin:$PATH \
    PYTHONPATH=/app

# Copy application code with proper ownership
COPY --chown=genesis:genesis . .

# Install the package locally as user
USER genesis
RUN pip install --no-cache-dir --user -e .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/tmp /app/cache && \
    chmod 755 /app/logs /app/tmp /app/cache

# Expose ports (documentation only, doesn't grant privileges)
EXPOSE 8000
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run as non-root user
USER genesis

# Set the command to run when the container starts
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
