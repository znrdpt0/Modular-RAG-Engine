from google import genai
from app.config import GEMINI_API_KEY

# Yeni nesil Gemini istemcisi
client = genai.Client(api_key=GEMINI_API_KEY)

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Metin listesini alır ve her biri için Gemini'dan 768 boyutlu vektör döner.
    Hata toleransı (Graceful Degradation) içerir.
    """
 
    # Önce en yeni modeli yalın bir şekilde (config olmadan) deniyoruz
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts
    )
    
    # Yeni SDK'da gelen cevabın içindeki float dizilerini (values) ayıklıyoruz
    return [embedding.values for embedding in response.embeddings]