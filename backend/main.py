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
    
class NewFeedRequest(BaseModel):
    url: str
    category: str
    source_name: str

# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "Nomad Backend (Cloud Native) is Running 🚀"}

# RSS & AI Analysis Endpoints
@app.get("/feeds")
def get_feeds(category: str = "ALL"):
    """RSS akışlarını getirir"""
    return rss_service.fetch_feeds(category)

@app.post("/feeds/add")
def add_new_feed(request: NewFeedRequest):
    """Yeni RSS kaynağı ekler"""
    feed_id = rss_service.add_feed_to_db(request.url, request.category, request.source_name)
    if feed_id:
        return {"status": "success", "message": f"Feed added: {request.source_name}"}
    else:
        raise HTTPException(status_code=500, detail="Database error")

@app.get("/categories")
def get_categories():
    """Mevcut kategorileri listeler"""
    feeds = rss_service.get_db_feeds()
    categories = ["ALL"] + list(feeds.keys())
    return categories

@app.post("/analyze")
def analyze_news(request: AnalysisRequest):
    """Seçilen haberi AI'a gönderir"""
    result = ai_analyst.analyze_article(request.title, request.content)
    return result

# RAG & Memory Endpoints
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

@app.get("/graph-data")
def get_graph_data():
    """
    Obsidian benzeri Graph View için veri oluşturur.
    Hafızadaki (agent_memory) verileri çeker, ortak TAG'leri olanları bağlar.
    """
    nodes = []
    links = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Son 50 hafıza kaydını çek (Performans için limitli)
        cursor.execute("SELECT id, content FROM agent_memory ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
        
        # 1. Düğümleri (Nodes) Hazırla
        for row in rows:
            mem_id, content = row
            
            # İçerikten Tag'leri Ayıkla (Kaydederken özel format kullanacağız)
            # Beklenen Format: "Title... | Tags: A, B, C | Insight..."
            extracted_tags = []
            label = f"Memory #{mem_id}"
            
            if "Tags:" in content:
                try:
                    # Basit string parsing ile veriyi ayıklıyoruz
                    parts = content.split("|")
                    
                    # Başlık (İlk parça)
                    if len(parts) > 0:
                        label = parts[0].strip()[:20] + "..." 

                    # Tagler (Tags: ile başlayan parça)
                    tag_part = next((p for p in parts if "Tags:" in p), None)
                    if tag_part:
                        # Temizle: Tags: A, B, C -> ['A', 'B', 'C']
                        clean_tags = tag_part.replace("Tags:", "").strip()
                        extracted_tags = [t.strip() for t in clean_tags.split(",") if t.strip()]
                except:
                    pass

            nodes.append({
                "id": mem_id,
                "label": label,
                "full_content": content,
                "tags": extracted_tags,
                "val": 5 # Düğüm büyüklüğü
            })

        # 2. Bağlantıları (Links) Kur
        # İki düğümün ortak bir etiketi varsa aralarına çizgi çek
        # Ancok çok genel tagler (TECH, AI vb.) tek başına bağ kurmak için yeterli değil.
        BROAD_TAGS = {"TECH", "AI", "SCIENCE", "DEV", "GENERAL"}
        
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                node_a = nodes[i]
                node_b = nodes[j]
                
                # Kesişim kümesi (Ortak tagler)
                common = set(node_a['tags']).intersection(set(node_b['tags']))
                
                # Sadece birden fazla ortak tag varsa VEYA tek ortak tag "özel" (broad değil) ise bağla
                if len(common) >= 2 or (len(common) == 1 and list(common)[0] not in BROAD_TAGS):
                    links.append({
                        "source": node_a['id'],
                        "target": node_b['id'],
                        "color": "#06b6d4" # Neon mavi bağlantı
                    })

        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Graph Error: {e}")
    
    return {"nodes": nodes, "links": links}

# Veritabanı Bağlantısı
def get_db_connection():
    conn_string = "postgresql://postgres:mypassword@localhost:5432/nomad?sslmode=disable"
    return psycopg2.connect(conn_string)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
