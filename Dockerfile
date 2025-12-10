# Use Python 3.11 base image
FROM python:3.11-slim

# Install system dependencies for Playwright
# Install essential browser dependencies manually (playwright install-deps has issues with some packages)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libx11-6 \
    libxext6 \
    libxcb1 \
    libexpat1 \
    fonts-liberation \
    fonts-unifont \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and Chromium
RUN playwright install chromium

# Copy application code
COPY . .

# Set environment variable for headless mode
ENV PLAYWRIGHT_HEADLESS=true

# Run the worker
CMD ["python", "scripts/railway_worker.py"]

