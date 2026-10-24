# DataPulse Backend Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy packaging configuration and backend requirements
COPY pyproject.toml setup.py alembic.ini /app/
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application packages and assets
COPY __init__.py /app/__init__.py
COPY backend /app/backend
COPY src /app/src
COPY etl /app/etl
COPY ml /app/ml
COPY database /app/database
COPY scripts /app/scripts
COPY data /app/data
COPY models_artifacts /app/models_artifacts
COPY reports /app/reports

# Install local package in editable mode
RUN pip install --no-cache-dir -e .

EXPOSE 8000

# Auto-execute migrations, compile SQL views, run idempotent ETL, and start Uvicorn
CMD ["sh", "-c", "alembic upgrade head && python scripts/init_db.py && python -m etl.run && uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
