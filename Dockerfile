FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları (gerekirse)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# requirements.txt kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kodları ve dizinleri kopyala
COPY src/ ./src/
RUN mkdir -p /app/data

# Container ayağa kalktığında hem veri çekme hem tahmin scriptini sırayla çalıştır
CMD ["sh", "-c", "python src/fetch_data.py && python src/predict.py"]