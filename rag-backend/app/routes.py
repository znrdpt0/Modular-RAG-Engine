from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel # Bize gelen JSON formatını doğrulamak için
import uuid
from typing import Optional, List
from app.pdf_utils import extract_text_from_pdf, chunk_text
from app.embeddings import get_embeddings
from app.vector_store import upsert_documents
from app.rag import ask_question 

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Kullanıcıdan PDF alır, metni çıkarır, parçalar, vektörleştirir ve kaydeder.
    Opsiyonel olarak aramayı belirli bir belgeyle sınırlar.
    """
    # 1. PDF mi ?
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Sadece PDF dosyaları desteklenir.")

    try:
        # 2. PDF read
        file_bytes = await file.read()
        text = extract_text_from_pdf(file_bytes)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="PDF'ten anlamlı bir metin çıkarılamadı.")

        # 3. Chunking
        chunks = chunk_text(text)

        # 4. embedding(with gemini)
        vectors = get_embeddings(chunks)

        # 5.Vector Database
        ids = [str(uuid.uuid4()) for _ in chunks]# uniqe ID for each vector
        
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
    # Kullanıcının sorusunun formatını tanımlıyoruz

class ChatMessage(BaseModel):
    role: str   # "user" (kullanıcı) veya "model" (yapay zeka)
    text: str   # Mesajın içeriği

class QuestionRequest(BaseModel):
    query: str
    filename: Optional[str] = None
    history: Optional[List[ChatMessage]] = []

@router.post("/ask")
async def ask_endpoint(request: QuestionRequest):
    """
    Kullanıcıdan soru alır (query) ve RAG sistemiyle dökümandan cevap üretir.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Soru boş olamaz.")

    try:
        # RAG fonksiyonumuzu çağırıyoruz
        answer = ask_question(query=request.query, filename=request.filename)
        
        return StreamingResponse(answer, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Akış üretilirken hata oluştu: {str(e)}")