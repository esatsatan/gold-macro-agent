# Resmi ve hafif Python 3.11 slim imajını temel alıyoruz (RAM ve disk dostu)
FROM python:3.11-slim

# Çalışma dizinini /app olarak belirliyoruz
WORKDIR /app

# Önce sadece requirements.txt dosyasını kopyalıyoruz (Docker katman önbelleklemesi için)
COPY requirements.txt .

# pip önbelleğini (cache) diskte tutmadan paketleri hızlıca yüklüyoruz
RUN pip install --no-cache-dir -r requirements.txt

# Proje kaynak kodlarını container içine kopyalıyoruz
COPY src/ ./src/

# SQLite veritabanı ve kalıcı veriler için data dizinini oluşturuyoruz
RUN mkdir -p /app/data

# FastAPI servisinin dış dünyadan istek alabilmesi için 8000 portunu açıyoruz
EXPOSE 8000

# Container ayağa kalktığında uvicorn ile FastAPI sunucusunu başlatıyoruz
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]