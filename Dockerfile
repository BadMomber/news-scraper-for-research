FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libatspi2.0-0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 \
    libcairo2 && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir playwright pyyaml pytest

# Install Chromium for Playwright
RUN playwright install chromium

# Copy project files
COPY src/ src/
COPY main.py .
COPY pyproject.toml .
COPY tests/ tests/

# Default: run the crawler
CMD ["python", "main.py"]
