import os
from dotenv import load_dotenv

# .env dosyasındaki ortam değişkenlerini sisteme yükle
load_dotenv()

# OpenAI Ayarları
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Qdrant Ayarları
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# RAG Chunk Ayarları (Metinleri string'den integer'a çeviriyoruz)
try:
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
except ValueError:
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100

# Fail-Fast (Hızlı Çökme) Prensibi
if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-buraya-kendi-openai-api-anahtarini-yazacaksin":
    raise ValueError(
        "KRİTİK HATA: OPENAI_API_KEY bulunamadı veya değiştirilmedi! "
        "Lütfen .env dosyanızı kontrol edin."
    )