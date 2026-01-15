# APGI Framework Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM python:3.9-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements-minimal.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements-minimal.txt

# Production stage
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglx-mesa0 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user
RUN useradd --create-home --shell /bin/bash apgi

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=apgi:apgi . .

# Install the application
RUN pip install -e .

# Create necessary directories
RUN mkdir -p data results logs figures reports session_state apgi_outputs/{dashboard,exports,figures,reports} && \
    chown -R apgi:apgi /app

# Switch to non-root user
USER apgi

# Expose port for web interface (if applicable)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import apgi_framework; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "apgi_gui"]
