from google import genai
from app.config import GEMINI_API_KEY
from app.embeddings import get_embeddings
from app.vector_store import client, COLLECTION_NAME

# Gemini LLM istemcisini başlatıyoruz
llm_client = genai.Client(api_key=GEMINI_API_KEY)

def ask_question(query: str, limit: int = 3) -> str:
    """
    Kullanıcının sorusunu alır, Qdrant'ta arar ve Gemini'ye cevaplatır.
    """
    # 1. RETRIEVAL (Geri Getirme): Soruyu vektöre çevir
    # Dökümanları kaydederken kullandığımız AYNı fonksiyonu kullanıyoruz!
    query_vector = get_embeddings([query])[0]

    # 2. Qdrant'ta Anlamsal Arama (Semantic Search) yap
    search_results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit # En çok benzeyen 3 metin parçasını (chunk) getir
    )

    # 3. Gelen sonuçların içindeki orijinal metinleri (payload) ayıkla
    context_texts = [hit.payload["text"] for hit in search_results]
    
    # Metinleri arasına ayraç koyarak tek bir büyük metin haline getir
    context = "\n\n---\n\n".join(context_texts)

    # 4. GENERATION (Üretim): LLM için mükemmel, kısıtlayıcı bir Prompt hazırla
    prompt = f"""
    Sen uzman bir yapay zeka asistanısın. Aşağıda sana bazı referans döküman parçaları verilmiştir.
    Kullanıcının sorusunu SADECE bu referans dökümanlara dayanarak cevapla. 
    Eğer sorunun cevabı dökümanlarda yoksa, "Bunun cevabını yüklenen dökümanda bulamadım." de ve asla kendi bilginden uydurma (hallucination yapma).

    Referans Dökümanlar:
    {context}

    Kullanıcının Sorusu: {query}
    """

    # 5. Gemini'ye soruyu sor (En hızlı model olan gemini-2.5-flash'i kullanıyoruz)
    response = llm_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )

    return response.text