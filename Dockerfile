# Multi-stage Dockerfile for Context App
# Builder stage for dependencies
FROM python:3.12-alpine AS builder

WORKDIR /app

# Install system dependencies needed for Python packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    && pip install --no-cache-dir --upgrade pip

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.12-alpine AS runtime

WORKDIR /app

# Install runtime system dependencies
RUN apk add --no-cache \
    libffi \
    openssl \
    && addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Ensure Python can find user-installed packages
ENV PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/root/.local/lib/python3.12/site-packages:$PYTHONPATH

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY favorites/ ./favorites/

# Create necessary directories and set permissions
RUN mkdir -p /app/favorites/logos /app/logos \
    && chown -R appuser:appgroup /app \
    && chmod -R 755 /app

# Create volume mount point for logos (persistent storage)
VOLUME ["/app/favorites/logos", "/app/logos"]

# Switch to non-root user
USER appuser

# Expose Flask port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5000/api/data || exit 1

# Run the application
CMD ["python", "backend/app.py"]