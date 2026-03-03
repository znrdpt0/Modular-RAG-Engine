from google import genai
from qdrant_client.http import models #Qdrant filtreleme
from app.config import GEMINI_API_KEY
from app.embeddings import get_embeddings
from app.vector_store import client, COLLECTION_NAME

# Gemini LLM istemcisini başlatıyoruz
llm_client = genai.Client(api_key=GEMINI_API_KEY)

def ask_question(query: str, limit: int = 3, filename: str = None, history : list = None):
    """
    Kullanıcının sorusunu vectöre çevir semantik arama yap en yakın 3 chunkı getir.
    """
    # 1. RETRIEVAL 
    query_vector = get_embeddings([query])[0]#ilk ve tek soru için [0] girdim
    
    #1.1 Search filtreleme eklendi.
    search_filter = None
    if filename :
        print(f"Filtre aktif: Sadece '{filename}' dosyası içinde aranıyor...")
        search_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="source", # Kaydederken kullandığımız payload anahtarı
                    match=models.MatchValue(value=filename) # Birebir eşleşme
                )
            ]
        )
    # 2. Semantic Search
    search_results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        query_filter=search_filter,
        limit=limit # En çok benzeyen 3 chunk
    )

    # 3. Gelen sonuçların içindeki orijinal metinleri (payload) ayıkla.
    context_texts = [hit.payload["text"] for hit in search_results]
    
    # LLM karıştırmasın diye chunkları böl.
    context = "\n\n---\n\n".join(context_texts)

    history_text = ""
    if history:
        history_text = "ÖNCEKİ SOHBET GEÇMİŞİ:\n"
        for msg in history:
            role_name = "Kullanıcı" if msg.role == "user" else "Asistan"
            history_text += f"{role_name}: {msg.text}\n"
        history_text += "\n" # Araya boşluk koyalım

    # 4. GENERATION: LLM için mükemmel, kısıtlayıcı bir Prompt hazırla
    prompt = f"""
    Sen uzman bir yapay zeka asistanısın. Aşağıda sana bazı referans döküman parçaları ve önceki sohbet geçmişi verilmiştir.
    Kullanıcının GÜNCEL sorusunu SADECE bu dökümanlara ve bağlama dayanarak cevapla.
    Eğer sorunun cevabı dökümanlarda yoksa, "Bunun cevabını yüklenen dökümanda bulamadım." de ve asla kendi bilginden uydurma (hallucination yapma).
     
    {history_text}

    Referans Dökümanlar:
    {context}

    Kullanıcının Sorusu: {query}
    """

    # 5. LLM'e soruyu yönelt
    response = llm_client.models.generate_content_stream(
        model='gemini-2.5-flash',
        contents=prompt
    )
    

    for chunk in response:
        if chunk.text:
            yield chunk.text