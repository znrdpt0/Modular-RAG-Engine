from google import genai
from app.config import GEMINI_API_KEY

# Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Metin listesini alır ve her biri için Gemini'dan 3072 boyutlu vektör döner.
    """
 
    # En yeni modeli çağır
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts
    )
    
    # SDK'dan gelen cevabın içindeki float dizilerini (values) ayıklıyoruz
    return [embedding.values for embedding in response.embeddings]

