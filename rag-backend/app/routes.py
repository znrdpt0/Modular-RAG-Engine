from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
from app.pdf_utils import extract_text_from_pdf, chunk_text
from app.embeddings import get_embeddings
from app.vector_store import upsert_documents

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Kullanıcıdan PDF alır, metni çıkarır, parçalar, vektörleştirir ve kaydeder.
    """
    # 1. Güvenlik ve Doğrulama
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Sadece PDF dosyaları desteklenir.")

    try:
        # 2. Dosyayı belleğe al ve metni çıkar
        file_bytes = await file.read()
        text = extract_text_from_pdf(file_bytes)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="PDF'ten anlamlı bir metin çıkarılamadı.")

        # 3. Metni lokmalara (chunk) böl
        chunks = chunk_text(text)

        # 4. Parçaları OpenAI ile vektörlere çevir
        vectors = get_embeddings(chunks)

        # 5. Veritabanı için benzersiz ID'ler ve Payload (orijinal metin) hazırlığı
        # Qdrant her bir vektör için benzersiz bir ID (UUID) ister
        ids = [str(uuid.uuid4()) for _ in chunks]
        
        # Arama yaptığımızda bize bu metinler ve dosya adı geri dönecek
        payloads = [{"text": chunk, "source": file.filename} for chunk in chunks]

        # 6. Qdrant'a kaydet
        upsert_documents(vectors=vectors, payloads=payloads, ids=ids)

        return {
            "message": "Belge başarıyla işlendi ve veritabanına kaydedildi.",
            "filename": file.filename,
            "chunks_created": len(chunks)
        }
    
    except Exception as e:
        # Production-ready hata yakalama
        raise HTTPException(status_code=500, detail=f"İşlem sırasında bir hata oluştu: {str(e)}")