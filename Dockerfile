FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (ffmpeg for audio conversion)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install only faster-whisper dependencies
RUN pip3 install --no-cache-dir \
    faster-whisper \
    sqlalchemy \
    google-generativeai \
    python-dotenv

# Copy application code
COPY . .

# Set environment variables for faster-whisper
ENV PYTHONUNBUFFERED=1
ENV WHISPER_ENGINE=faster
ENV FASTER_WHISPER_MODEL=small
ENV FASTER_WHISPER_COMPUTE_TYPE=int8
ENV WHISPER_DEVICE=cpu

# Create mount point for music files
VOLUME ["/music"]

# Run the application
CMD ["python3", "main.py"]