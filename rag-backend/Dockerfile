FROM python:3.11-slim

WORKDIR /app

# Bağımlılıklar: Önce requirements.txt
# (Sadece bunu önce kopyalamak Docker'ın cache mekanizmasını hızlandırır)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#  Kodları kopyala
COPY . .

# FastAPI 8000 portunda çalışıyor
EXPOSE 8000

# Sunucuyu başlat
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]