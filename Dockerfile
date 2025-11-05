FROM python:3.9-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Minimal system deps
RUN apt-get update && apt-get upgrade -y && \
    apt-get install --no-install-recommends -y \
    ffmpeg \
    libpq-dev \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for better caching
COPY requirements.txt ./
RUN pip3 install --upgrade pip setuptools && \
    pip3 install -U -r requirements.txt

# Copy project
COPY . .

# Run as worker
CMD ["python3","-m","innexiaBot"]
