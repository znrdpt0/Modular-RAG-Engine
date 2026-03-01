from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import router
from app.vector_store import init_vector_store

# Lifespan: Uygulama başlarken ve kapanırken çalışacak olayları yönetir
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Uygulama BAŞLARKEN çalışacak kod:
    print("Sistem başlatılıyor, veritabanı kontrol ediliyor...")
    init_vector_store()
    yield
    # Uygulama KAPANIRKEN çalışacak kod (Şu an boş ama ileride bağlantıları kapatmak için kullanılabilir)
    print("Sistem kapatılıyor...")

# Uygulama örneğini oluştur
app = FastAPI(
    title="RAG Backend MVP",
    description="Minimal, temiz ve deploy edilebilir RAG sistemi.",
    version="1.0.0",
    lifespan=lifespan
)

# Yazdığımız rotaları (upload, vb.) ana uygulamaya bağla
app.include_router(router)

# Health-Check Endpoint'i (Sunucunun ayakta olup olmadığını kontrol etmek için)
@app.get("/")
def health_check():
    return {"status": "ok", "message": "RAG Backend tıkır tıkır çalışıyor 🚀"}