# Use Python 3.11 base image
FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and Chromium
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . .

# Set environment variable for headless mode
ENV PLAYWRIGHT_HEADLESS=true

# Run the worker
CMD ["python", "scripts/railway_worker.py"]

