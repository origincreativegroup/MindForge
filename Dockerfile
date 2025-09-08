# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry

# Install dependencies early to leverage Docker cache
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-interaction --no-ansi

# Copy application code
COPY . /app

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "apps.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
