# Multi-stage Dockerfile for {{ cookiecutter.project_name }} Backend

# Stage 1: Base image with Python {{ cookiecutter.python_version }}
FROM python:{{ cookiecutter.python_version }}-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:$PATH"


# Stage 2: Dependencies
FROM base AS dependencies

# Copy uv files and README for dependency installation
COPY pyproject.toml uv.lock README.md ./

# Sync dependencies using uv
RUN uv sync --frozen --no-dev


# Stage 3: Development image
FROM dependencies AS development

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run with hot-reload for development
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# Stage 4: Production image
FROM dependencies AS production

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run with production settings
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
