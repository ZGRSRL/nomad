import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv
import psycopg2
import rss_service
import ai_analyst

# .env dosyasını yükle
load_dotenv()

app = FastAPI(title="Nomad API 🦅")

# CORS (Frontend'in Backend'e erişmesi için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme aşamasında herkese açık
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini Yapılandırması
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("UYARI: GEMINI_API_KEY bulunamadı!")
else:
    genai.configure(api_key=API_KEY)

# --- REQUEST MODELS ---
class SummarizeRequest(BaseModel):
    text: str

class QuestionRequest(BaseModel):
    question: str

class SaveRequest(BaseModel):
    text: str

class AnalysisRequest(BaseModel):
    title: str
    content: str

# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "Nomad Backend (Cloud Native) is Running 🚀"}

# RSS & AI Analysis Endpoints (NEW)
@app.get("/feeds")
def get_feeds(category: str = "ALL"):
    """RSS akışlarını getirir"""
    return rss_service.fetch_feeds(category)

@app.post("/analyze")
def analyze_news(request: AnalysisRequest):
    """Seçilen haberi AI'a gönderir"""
    result = ai_analyst.analyze_article(request.title, request.content)
    return result

# RAG & Memory Endpoints (EXISTING)
@app.post("/summarize")
def summarize_text(request: SummarizeRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key eksik.")
    
    try:
        # En hızlı ve ucuz model: Listeden bulunan gecerli model
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        prompt = f"Aşağıdaki metni Türkçe olarak, maddeler halinde özetle:\n\n{request.text}"
        response = model.generate_content(prompt)
        
        return {"summary": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
def chat_with_memory(request: QuestionRequest):
    """
    Nomad'ın hafızasıyla konuşmak için endpoint.
    """
    from rag_service import ask_nomad
    answer = ask_nomad(request.question)
    return {"answer": answer}

@app.post("/save")
def save_to_memory(request: SaveRequest):
    # 1. Metnin Vektörünü Üret
    from embedding_service import generate_embedding
    vector = generate_embedding(request.text)
    
    if not vector:
        raise HTTPException(status_code=500, detail="Vektör üretilemedi.")
    
    try:
        # 2. Veritabanına Kaydet
        conn = get_db_connection()
        cursor = conn.cursor()
        
        insert_query = "INSERT INTO agent_memory (content, embedding) VALUES (%s, %s) RETURNING id;"
        cursor.execute(insert_query, (request.text, str(vector)))
        memory_id = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"status": "success", "id": memory_id, "message": "Bilgi Nomad'ın hafızasına kazındı."}
        
    except Exception as e:
        print(f"DB Error: {e}")
        raise HTTPException(status_code=500, detail=f"Veritabanı Hatası: {str(e)}")

# Veritabanı Bağlantısı
def get_db_connection():
    conn_string = "postgresql://postgres:mypassword@localhost:5432/nomad?sslmode=disable"
    return psycopg2.connect(conn_string)

if __name__ == "__main__":
    import uvicorn
    # Localde geliştirirken 8000 portunu kullanıyoruz
    uvicorn.run(app, host="0.0.0.0", port=8000)
