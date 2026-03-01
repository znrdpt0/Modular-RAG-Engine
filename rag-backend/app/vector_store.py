from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.config import QDRANT_URL


client = QdrantClient(url=QDRANT_URL)

COLLECTION_NAME = "rag_documents_gemini"

def init_vector_store():
    """
    Uygulama başladığında veritabanında gerekli 'tabloyu' (collection) oluşturur.
    """
    # Mevcut koleksiyonları kontrol et
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)

    if not exists:
        print(f"'{COLLECTION_NAME}' koleksiyonu oluşturuluyor...")
        # Koleksiyon oluşturma: SQL'deki 'CREATE TABLE' gibi düşün.
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=3072, #Gemini 3072 boyutlu çıktı verir
                distance=models.Distance.COSINE # Benzerlik ölçüm yöntemi
            )
        )
        print("Koleksiyon başarıyla oluşturuldu.")

def upsert_documents(vectors, payloads, ids):
    """
    Vektörleri ve ilgili metin parçalarını veritabanına kaydeder.
    """
    client.upsert( # Update + Insert birleşimi
        collection_name=COLLECTION_NAME,
        points=models.Batch(
            ids=ids,
            vectors=vectors,
            payloads=payloads
        )
    )