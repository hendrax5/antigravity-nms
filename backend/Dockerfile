# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies (required for some netmiko or psycopg compilations)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies (Update to psycopg3 compatible requirements)
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose API port
EXPOSE 8000

# Entrypoint will be defined in docker-compose depending on API or Worker service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
