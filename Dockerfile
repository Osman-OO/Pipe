# Advanced Data Analytics Pipeline - Production Docker Image
# Author: Osman Abdullahi
# Email: Osmandabdullahi@gmail.com

FROM python:3.11-slim

# Set metadata
LABEL maintainer="Osman Abdullahi <Osmandabdullahi@gmail.com>"
LABEL description="Advanced Data Analytics Pipeline - Professional Business Intelligence Platform"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs reports data/output

# Set permissions
RUN chmod +x run_pipe

# Create non-root user for security
RUN useradd -m -u 1000 analytics && \
    chown -R analytics:analytics /app
USER analytics

# Expose dashboard port
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8050/ || exit 1

# Default command
CMD ["python", "-m", "pipe.analytics_app", "--dashboard", "--port", "8050"]
