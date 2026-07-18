# Multi-stage build
FROM python:3.10-slim AS builder

WORKDIR /app

# Sistem bağımlılıkları - DÜZELTİLDİ
RUN apt-get update && apt-get install -y \
    ghostscript \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama
COPY app/ ./app/
COPY data/ ./data/
COPY logs/ ./logs/
COPY app/config.json .

# Streamlit config
RUN mkdir -p .streamlit
RUN echo "[server]\nheadless = true\nenableCORS = false\nenableXsrfProtection = false\n" > .streamlit/config.toml

# Port
EXPOSE 8501

# Start
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]