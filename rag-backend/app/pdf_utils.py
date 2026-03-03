import fitz  # PyMuPDF
from typing import List
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Byte formatında gelen PDF'i doğrudan bellekten okuyarak texti çıkarrı.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text() + "\n"#sayfa atlaması
    return text

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Metni word sayısına böler.
    """
    
    words = text.split()
    chunks = []
    
    # overlap
    for i in range(0, len(words), max(1, chunk_size - overlap)):
        chunk_words = words[i : i + chunk_size]
        chunk_text = " ".join(chunk_words)
        
        if chunk_text.strip():
            chunks.append(chunk_text.strip())
            
    return chunks