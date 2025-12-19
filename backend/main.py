import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv
import psycopg2
import rss_service
import scraper_service
import ai_analyst
import trend_service
import drive_service

# .env dosyasını yükle
from pathlib import Path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="Nomad API 🦅")

# CORS (Frontend'in Backend'e erişmesi için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Herkese açık (Credentials False olduğu için çalışır)
    allow_credentials=False,
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

class ScanRequest(BaseModel):
    url: str

class ReportRequest(BaseModel):
    title: str
    content: str

# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "Nomad Backend (Cloud Native) is Running 🚀"}

@app.get("/admin/init-db")
def init_database_tables():
    """Veritabanı Tablolarını Cloud Üzerinden Oluşturur (Migration)"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. FEEDS TABLE
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feeds (
                id SERIAL PRIMARY KEY,
                url TEXT UNIQUE NOT NULL,
                categoryvb TEXT,
                source_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 2. AGENT MEMORY TABLE
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agent_memory (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding TEXT, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        cur.close()
        return {"status": "SUCCESS", "message": "Tables 'feeds' and 'agent_memory' ensure created."}
        
    except Exception as e:
        if conn: conn.rollback()
        return {"status": "FAILED", "error": str(e)}
    finally:
        if conn: conn.close()

@app.get("/debug-db")
def debug_database():
    """Veritabanı bağlantısını test eder ve değişkenleri kontrol eder"""
    import os
    db_pass = os.getenv("DB_PASSWORD", "")
    db_url = os.getenv("DB_URL", "")
    
    debug_info = {
        "DB_PASSWORD_LEN": len(db_pass) if db_pass else 0,
        "DB_PASSWORD_START": db_pass[:2] if db_pass else "NONE",
        "DB_PASSWORD_END": db_pass[-2:] if db_pass else "NONE",
        "DB_URL_PRESENT": bool(db_url),
        "HOST": os.getenv("DB_HOST"),
    }
    
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "CONNECTED", "debug": debug_info}
    except Exception as e:
        return {"status": "FAILED", "error": str(e), "debug": debug_info}

# RSS & AI Analysis Endpoints
@app.get("/feeds")
def get_feeds(category: str = "ALL"):
    """RSS akışlarını getirir"""
    return rss_service.fetch_feeds(category)

@app.get("/sources")
def get_feed_sources():
    """Admin: Kayıtlı tüm RSS kaynaklarını listeler"""
    return rss_service.get_db_feeds(active_only=False)

@app.get("/trends")
async def get_global_trends():
    """Son haberlerden trend analizi yapar"""
    # 1. Tüm haberleri çek
    all_news = rss_service.fetch_feeds("ALL")
    # 2. Trend servisine gönder
    trends = trend_service.analyze_trends(all_news)
    return trends

@app.post("/feeds/add")
def add_new_feed(request: NewFeedRequest):
    """Yeni RSS kaynağı ekler (Gelişmiş - Duplicate Check)"""
    conn = None
    try:
        # 1. Önce Linki Doğrula
        # Bu işlem uzun sürebilir, timeout yiyebilir, DB'den önce yapılması iyi.
        is_valid, msg = rss_service.verify_rss_url(request.url)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"RSS Error: {msg}")

        conn = get_db_connection()
        cur = conn.cursor()

        # 2. Bu link zaten var mı?
        cur.execute("SELECT id FROM feeds WHERE url = %s", (request.url,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Bu kaynak zaten ekli Kaptan!")

        # 3. Yoksa ekle
        cur.execute(
            "INSERT INTO feeds (url, categoryvb, source_name) VALUES (%s, %s, %s) RETURNING id",
            (request.url, request.category.upper(), request.source_name.upper())
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return {"status": "success", "message": f"Feed added: {request.source_name}", "id": new_id}

    except HTTPException:
        if conn: conn.rollback()
        raise # Kendi fırlattığımız hataları olduğu gibi geç
    except Exception as e:
        if conn: conn.rollback()
        print(f"CRITICAL ERROR in add_new_feed: {e}")
        # Hata detayını return et ki debug edebilelim
        raise HTTPException(status_code=500, detail=f"System Crash: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.get("/categories")
def get_categories():
    """Mevcut kategorileri dinamik olarak listeler"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT categoryvb FROM feeds")
        cats = [row[0] for row in cur.fetchall()]
        if "ALL" not in cats: cats.insert(0, "ALL")
        return cats
    except Exception as e:
        print(f"Cat Error: {e}")
        return ["ALL", "TECH", "CYBERSEC"] # Hata olursa varsayılanları dön
    finally:
        cur.close()
        conn.close()

@app.delete("/feeds/{feed_id}")
def delete_feed(feed_id: int):
    """Feed'i kalici olarak siler"""
    if rss_service.delete_feed_from_db(feed_id):
        return {"status": "success", "message": f"Feed {feed_id} deleted."}
    else:
        raise HTTPException(status_code=404, detail="Feed bulunamadı veya silinemedi.")

@app.post("/analyze")
def analyze_news(request: AnalysisRequest):
    """Seçilen haberi AI'a gönderir"""
    result = ai_analyst.analyze_article(request.title, request.content)
    return result

@app.post("/scan")
def deep_scan_url(request: ScanRequest):
    """Verilen URL'i tarar ve analiz eder"""
    scraped_data = scraper_service.scrape_url(request.url)
    
    if not scraped_data:
        raise HTTPException(status_code=400, detail="URL taranamadı veya içerik alınamadı.")
        
    # AI Analizi
    analysis = ai_analyst.analyze_article(scraped_data['title'], scraped_data['content'])
    
    # Orijinal linki de analize ekle ki kaydederken kullanabilelim
    analysis['link'] = request.url
    
    return analysis

@app.get("/graph-data")
def get_graph_data():
    """Neural Graph için veritabanından node ve linkleri çeker"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 1. Hafızadaki tüm verileri çek (content ve embedding lazım değil, id ve content yeter)
        cur.execute("SELECT id, content FROM agent_memory ORDER BY created_at DESC LIMIT 50")
        rows = cur.fetchall()
        
        nodes = []
        links = []
        
        # Basit bir ilişkilendirme (Tag veya anahtar kelimeye göre)
        # Gerçek bir sistemde embedding distance kullanılabilir.
        # Şimdilik: "TECH", "AI", "SPACE", "SECURITY" kelimelerini içerenleri birbirine bağlayalım.
        
        keywords = ["AI", "DATA", "ROBOT", "SPACE", "SECURITY", "CYBER", "CODE", "SYSTEM", "FUTURE", "MODEL"]
        
        for r in rows:
            mem_id = r[0]
            text = r[1]
            title = text.split('|')[0][:30] + "..." if '|' in text else text[:30] + "..."
            
            # Node ekle
            nodes.append({
                "id": str(mem_id),
                "name": title,
                "group": "memory",
                "val": 5
            })
            
            # Link oluştur (Basit anahtar kelime eşleşmesi)
            found_keys = [k for k in keywords if k in text.upper()]
            # Her bir keyword için sanal bir grup node'u oluşturabiliriz veya birbirlerine bağlayabiliriz.
            # Şimdilik rastgele bir önceki node'a bağlayalım ki ağ oluşsun (Demo)
            import random
            if len(nodes) > 1 and random.random() > 0.5:
                target = nodes[random.randint(0, len(nodes)-2)]
                links.append({
                    "source": str(mem_id),
                    "target": target["id"]
                })
                
        # Merkez Node
        nodes.append({"id": "CORE", "name": "NOMAD CORE", "group": "core", "val": 15})
        for n in nodes[:5]: # İlk 5'i merkeze bağla
            if n["id"] != "CORE":
                links.append({"source": n["id"], "target": "CORE"})

        return {"nodes": nodes, "links": links}

    except Exception as e:
        print(f"Graph Error: {e}")
        return {"nodes": [], "links": []}
    finally:
        cur.close()
        conn.close()

@app.get("/stats")
def get_dashboard_stats():
    from collections import Counter
    import re
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 1. Klasik Sayaçlar
        cur.execute("SELECT COUNT(*) FROM feeds")
        total_sources = cur.fetchone()[0]
        
        try:
            cur.execute("SELECT COUNT(*) FROM agent_memory")
            total_intel = cur.fetchone()[0]
        except:
            total_intel = 0

        # --- 2. SQL TABANLI TREND ANALİZİ (OPTIMIZED) ---
        # Son 100 haberin başlığını çek
        dominant_trend = "WAITING DATA..."
        try:
            cur.execute("SELECT content FROM agent_memory ORDER BY created_at DESC LIMIT 100")
            rows = cur.fetchall()
            
            if rows:
                all_text = " ".join([r[0] for r in rows]).lower()
                
                # Basit Kelime Frekansı
                words = re.findall(r'\w+', all_text)
                ignored = {'the', 'and', 'for', 'with', 'summary', 'insight', 'tags', 'title', 'date', 'source', 'to', 'of', 'in', 'a', 'is', 'link', 'http', 'https', 'com', 'org', 'net', 'www', 'news', 'feed'}
                filtered_words = [w for w in words if w not in ignored and len(w) > 3]
                
                if filtered_words:
                    most_common = Counter(filtered_words).most_common(1)
                    dominant_trend = most_common[0][0].upper()
        except Exception as e:
            print(f"Trend Calc Error: {e}")

        # 3. Son Haberler
        recent_alerts = []
        try:
            cur.execute("SELECT content, created_at FROM agent_memory ORDER BY created_at DESC LIMIT 5")
            for r in cur.fetchall():
                parts = r[0].split('|')
                title = parts[0][:50] + "..." if len(parts) > 0 else "Signal"
                recent_alerts.append({"title": title, "time": str(r[1])})
        except:
            pass

        return {
            "total_sources": total_sources,
            "total_intel": total_intel,
            "top_trend": dominant_trend,
            "system_status": "OPTIMIZED",
            "recent_alerts": recent_alerts
        }
    except Exception as e:
        print(f"Stats Error: {e}")
        return {"total_sources": 0, "total_intel": 0, "top_trend": "OFFLINE", "system_status": "ERROR", "recent_alerts": []}
    finally:
        cur.close()
        conn.close()

# RAG & Memory Endpoints
@app.post("/summarize")
def summarize_text(request: SummarizeRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key eksik.")
    
    try:
        # Try different model names in order of preference
        model_names = [
            "gemini-2.0-flash-exp", # Latest/Fastest
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-pro"
        ]
        model = None
        
        last_error = None
        for name in model_names:
            try:
                model = genai.GenerativeModel(name)
                # Test generation call? No, usually unnecessary overhead, but good for validation.
                # Just break if initialization succeeded (which is lazy in this lib, so maybe redundant).
                # But let's proceed to generate with the first successful model.
                prompt = f"Aşağıdaki metni Türkçe olarak, maddeler halinde özetle:\n\n{request.text}"
                response = model.generate_content(prompt)
                return {"summary": response.text}
            except Exception as e:
                # print(f"Model {name} failed: {e}")
                last_error = e
                continue
        
        if last_error:
            raise last_error
            
        return {"summary": "No model available."}
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

@app.post("/upload-report")
def upload_intelligence_report(request: ReportRequest):
    """
    Raporu Google Drive'a (Docs formatında) yükler.
    HTML içeriği alır, Drive API ile dönüştürüp 'Nomad Intelligence' klasörüne atar.
    """
    result = drive_service.upload_html_as_doc(request.title, request.content)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
        
    return result

@app.get("/stats")
def get_dashboard_stats():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 1. Toplam Kaynak
        cur.execute("SELECT COUNT(*) FROM feeds")
        total_sources = cur.fetchone()[0]

        # 2. İşlenen Veri
        try:
            cur.execute("SELECT COUNT(*) FROM agent_memory")
            total_intel = cur.fetchone()[0]
        except:
            total_intel = 0

        # 3. DOMINANT TREND (En çok hangi kategoriden haber var?)
        dominant_trend = "GENEL"
        try:
            cur.execute("""
                SELECT categoryvb, COUNT(*) as count 
                FROM feeds 
                GROUP BY categoryvb 
                ORDER BY count DESC 
                LIMIT 1
            """)
            row = cur.fetchone()
            if row:
                dominant_trend = row[0] # Örn: AI, TECH, SCIENCE
        except:
            pass
        
        # 4. Son Kritik Gelişmeler (Yüksek skorlu son haberler)
        recent_alerts = []
        try:
            # Sadece tehdit değil, skoru yüksek (önemli) haberleri çekelim
            cur.execute("SELECT content, created_at FROM agent_memory ORDER BY created_at DESC LIMIT 5")
            rows = cur.fetchall()
            for r in rows:
                parts = r[0].split('|')
                title = parts[0] if len(parts) > 0 else "Signal"
                recent_alerts.append({"title": title, "time": str(r[1])})
        except:
            pass

        return {
            "total_sources": total_sources,
            "total_intel": total_intel,
            "top_trend": dominant_trend,  # <-- YENİ: En popüler konu
            "system_status": "ONLINE",
            "recent_alerts": recent_alerts
        }
    except Exception as e:
        print(f"Stats Error: {e}")
        return {"total_sources": 0, "total_intel": 0, "top_trend": "ANALYZING", "system_status": "OFFLINE", "recent_alerts": []}
    finally:
        cur.close()
        conn.close()

# Veritabanı Bağlantısı
# Veritabanı Bağlantısı - Robust
def get_db_connection():
    from urllib.parse import urlparse
    
    # 1. Direct Env Vars (Safest for special chars)
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER", "postgres")
    db_name = os.getenv("DB_NAME", "postgres")
    
    if db_pass and db_host:
        return psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_pass,
            host=db_host,
            port=5432,
            sslmode="require"
        )

    # 2. Fallback to URL Parsing
    db_url = os.getenv("DB_URL")
    if not db_url:
        return psycopg2.connect("postgresql://postgres:mypassword@localhost:5432/nomad?sslmode=disable")
        
    try:
        # Check if sslmode is explicitly disabled in the URL string
        ssl_mode = "require"
        if "sslmode=disable" in db_url:
            ssl_mode = "disable"

        result = urlparse(db_url)
        if result.username and result.password:
            return psycopg2.connect(
                database=result.path[1:] if result.path else "postgres",
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port,
                sslmode=ssl_mode
            )
        else:
            return psycopg2.connect(db_url)
    except Exception as e:
        print(f"Connection String Parsing Error: {e}")
        # Ensure fallback connects even if parsing fails
        return psycopg2.connect(db_url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
