FROM ubuntu:22.04

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update system and install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY scrapers/ ./scrapers/
COPY init_db.py .

# Create data directory for database
RUN mkdir -p /data

# Set environment variables for database path
ENV DB_PATH=/data/ski.db

# Default command (can be overridden)
CMD ["python3", "-c", "print('Ski scraper container ready. Use docker-compose to run specific scrapers.')"]