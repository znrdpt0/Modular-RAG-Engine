import os
from dotenv import load_dotenv

load_dotenv()

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

try:
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
except ValueError:
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100

if not GEMINI_API_KEY:
    raise ValueError("KRİTİK HATA: GEMINI_API_KEY bulunamadı! Lütfen .env dosyanızı kontrol edin.")