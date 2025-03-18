# Stage 1: Build stage
FROM python:3.13-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=2.1.1
ENV PATH="/root/.local/bin:${PATH}"
ENV PIPENV_VENV_IN_PROJECT=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --user poetry==$POETRY_VERSION

# Set working directory
WORKDIR /app

# Copy only the dependency files first to leverage Docker layer caching
COPY pyproject.toml poetry.lock ./

COPY . .

# Stage 2: Runtime stage
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:${PATH}"

# Install runtime dependencies (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from the builder stage
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

# Set working directory
WORKDIR /app

RUN poetry install --no-root --no-interaction --no-ansi

# Expose the port the app runs on
EXPOSE 8000

# Run the application with Gunicorn
ENTRYPOINT ["poetry run gunicorn", "--bind", "0.0.0.0:8000", "mb_mms.wsgi:app"]
