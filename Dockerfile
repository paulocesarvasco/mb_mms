# Stage 1: Build stage
FROM python:3.13-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=2.1.1
ENV PATH="/root/.local/bin:${PATH}"


# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry with pip --user
RUN pip install --user poetry==$POETRY_VERSION

# Verify Poetry installation
RUN poetry --version

# Set working directory
WORKDIR /app

# Copy only the dependency files first to leverage Docker layer caching
COPY pyproject.toml poetry.lock ./

# Install dependencies with Poetry
RUN poetry install --no-interaction --no-ansi --no-root

RUN poetry show

# Copy the rest of the application code
COPY . .

# Stage 2: Runtime stage
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=2.1.1
ENV PATH="/root/.local/bin:${PATH}"


# Install runtime dependencies (if any)
RUN apt-get update && apt-get install -y --no-install-recommends

RUN pip install --user poetry==$POETRY_VERSION

# Copy installed dependencies from the builder stage
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

# Set working directory
WORKDIR /app

RUN ls -la

RUN poetry install --no-interaction --no-ansi --no-root

# Expose the port the app runs on
EXPOSE 8000

# Run the application with Gunicorn
CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "mb_mms.wsgi:app"]
