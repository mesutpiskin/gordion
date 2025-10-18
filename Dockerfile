FROM python:3.8-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs config

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CHECK_INTERVAL=300
ENV DRY_RUN=false

# Default command to run the agent
CMD ["python3", "src/main.py"]