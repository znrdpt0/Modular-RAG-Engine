# 1. Temel imaj: Python'ın hafif bir versiyonunu kullanıyoruz
FROM python:3.11-slim

# 2. Çalışma dizini: Konteyner içinde kodların duracağı yer
WORKDIR /app

# 3. Bağımlılıklar: Önce requirements.txt'yi kopyalayıp kuruyoruz
# (Sadece bunu önce kopyalamak Docker'ın cache mekanizmasını hızlandırır)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Kodları kopyala: Kendi yazdığın tüm python dosyalarını içeri aktar
COPY . .

# 5. Dış dünyaya açılan kapı: FastAPI 8000 portunda çalışıyor
EXPOSE 8000

# 6. Çalıştırma komutu: Sunucuyu başlat
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]