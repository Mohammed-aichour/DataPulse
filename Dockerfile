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

# Copy backend requirements
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy source code, data, database, models
COPY backend /app/backend
COPY src /app/src
COPY database /app/database
COPY data /app/data
COPY models_artifacts /app/models_artifacts
COPY reports /app/reports

EXPOSE 8000

# Run pipeline check & start uvicorn
CMD ["sh", "-c", "python -m src.pipeline.run && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"]
