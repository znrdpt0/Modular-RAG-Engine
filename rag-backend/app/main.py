from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.vector_store import init_vector_store

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Uygulama başlarken veritabınını ayağı kaldır
    print("Sistem başlatılıyor, veritabanı kontrol ediliyor...")
    init_vector_store()
    yield
    print("Sistem kapatılıyor...")

# Uygulama örneğini oluştur
app = FastAPI(
    title="RAG Backend MVP",
    description="Minimal, temiz ve deploy edilebilir RAG sistemi.",
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme aşamasında her yere açık bırakıyoruz.
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT vb. hepsine izin ver
    allow_headers=["*"],
)

app.include_router(router)

# Health-Check Endpoint
@app.get("/")
def health_check():
    return {"status": "ok", "message": "RAG Backend tıkır tıkır çalışıyor 🚀"}