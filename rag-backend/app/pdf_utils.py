import fitz  # PyMuPDF
import tiktoken
from typing import List
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Byte formatında gelen PDF'in içindeki metni hızlıca çıkarır.
    """
    # stream=pdf_bytes: PDF'i diske kaydetmeden doğrudan bellekten okuyoruz (Performans!)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Metni kelime (word) sayısına göre parçalara böler.
    Dış bir tokenizer kütüphanesine (tiktoken vb.) ihtiyaç duymaz, çok hızlıdır.
    """
    # Metni boşluklardan kelimelere ayır
    words = text.split()
    chunks = []
    
    # Kelime listesi üzerinde overlap (örtüşme) bırakarak ilerle
    for i in range(0, len(words), max(1, chunk_size - overlap)):
        chunk_words = words[i : i + chunk_size]
        chunk_text = " ".join(chunk_words)
        
        if chunk_text.strip():
            chunks.append(chunk_text.strip())
            
    return chunks