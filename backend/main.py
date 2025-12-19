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
import time

# --- CACHE ---
FEED_CACHE = {} # { "category": { "timestamp": 123, "data": [] } }
CACHE_DURATION = 900 # 15 minutes

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
async def get_feeds(category: str = "ALL", limit: int = 50, offset: int = 0):
    """RSS akışlarını getirir (Async + Cache + Pagination)"""
    
    current_time = time.time()
    cached = FEED_CACHE.get(category)
    
    # 1. Check Cache
    if cached and (current_time - cached["timestamp"] < CACHE_DURATION):
        print(f"⚡ Serving from CACHE ({category})")
        all_articles = cached["data"]
    else:
        # 2. Fetch (Async)
        print(f"🔄 Fetching Fresh Data ({category})...")
        try:
            all_articles = await rss_service.fetch_feeds_async(category)
            # Update Cache
            FEED_CACHE[category] = {
                "timestamp": current_time,
                "data": all_articles
            }
        except Exception as e:
            print(f"Fetch Error: {e}")
            if cached: return cached["data"] # Return stale data on error
            return []

    # 3. Apply Pagination
    # Frontend performance için slice ediyoruz
    return all_articles[offset : offset + limit]

@app.get("/trends")
async def get_global_trends():
    """Son haberlerden trend analizi yapar"""
    # 1. Tüm haberleri çek (Async)
    all_news = await rss_service.fetch_feeds_async("ALL")
    # 2. Trend servisine gönder
    trends = trend_service.analyze_trends(all_news)
    return trends

@app.post("/feeds/add")
def add_new_feed(request: NewFeedRequest):
    """Yeni RSS kaynağı ekler (Gelişmiş - Duplicate Check)"""
    # ... (Existing logic but ensuring imports align, keeping as is)
    # Reusing existing logic but verifying calls to rss_service
    # Since rss_service.verify_rss_url is synchronous, we can keep this sync or make it async.
    # FastAPI handles sync endpoints in threadpool, so it's fine.
    
    # 1. Validation
    is_valid, msg = rss_service.verify_rss_url(request.url)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"RSS Error: {msg}")

    # 2. Add to DB
    res = rss_service.add_feed_to_db(request.url, request.category, request.source_name)
    if not res:
        raise HTTPException(status_code=400, detail="Ekleme başarısız veya duplicate.")
    
    return {"status": "success", "message": f"Feed added: {request.source_name}", "id": res}

@app.delete("/feeds/{feed_id}")
def delete_feed(feed_id: int):
    """Admin: Bir kaynağı siler"""
    success = rss_service.delete_feed_from_db(feed_id)
    if not success:
        raise HTTPException(status_code=404, detail="Feed silinemedi veya bulunamadı.")
    return {"status": "success", "id": feed_id}

class FeedStatusRequest(BaseModel):
    is_active: bool

@app.put("/feeds/{feed_id}/status")
def toggle_feed_status(feed_id: int, status: FeedStatusRequest):
    """Admin: Bir kaynağı aktif/pasif yapar"""
    success = rss_service.toggle_feed_status(feed_id, status.is_active)
    if not success:
        raise HTTPException(status_code=404, detail="Feed güncellenemedi.")
    return {"status": "success", "id": feed_id, "is_active": status.is_active}

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

@app.post("/analyze")
def analyze_news(request: AnalysisRequest):
    """Seçilen haberi AI'a gönderir"""
    result = ai_analyst.analyze_article(request.title, request.content)
    
    # --- ACTION ENGINE TRIGGER ---
    if result.get("impact_score", 0) >= 80:
        print(f"🚀 ACTION ENGINE: High Impact ({result['impact_score']}) detected. Generating Report...")
        
        # HTML Rapor Hazırla
        report_html = f"""
        <h1>⚡ INTELLIGENCE ALERT: {result.get('impact_score')} / 100</h1>
        <h2>{request.title}</h2>
        <hr>
        <h3>🤖 AI Insight</h3>
        <p>{result.get('aiInsight')}</p>
        <h3>📝 Summary</h3>
        <p>{result.get('summary')}</p>
        <hr>
        <h3>Strategic Action</h3>
        <p><strong>{result.get('action')}</strong></p>
        <br>
        <small>Generated by Nomad Action Engine</small>
        """
        
        # Drive'a Yükle
        # Drive'a Yükle - DISABLED (User manually triggers Archive)
        # upload_res = drive_service.upload_html_as_doc(f"ALERT: {request.title}", report_html)
        
        # if upload_res.get("status") == "success":
        #     result["action_taken"] = "IMMEDIATE_REPORT_GENERATED"
        #     result["report_link"] = upload_res.get("link")
        # else:
        #     print(f"❌ UPLOAD FAILED DETAILS: {upload_res}")
        #     result["action_taken"] = "REPORT_FAILED"
        
        print("ℹ️ Auto-Upload skipped to prevent duplicates. User can Archive manually.")
        result["action_taken"] = "AUTO_UPLOAD_DISABLED"
            
    return result

@app.post("/scan")
def deep_scan_url(request: ScanRequest):
    """Verilen URL'i tarar ve analiz eder"""
    scraped_data = scraper_service.scrape_url(request.url)
    
    if not scraped_data:
        raise HTTPException(status_code=400, detail="URL taranamadı veya içerik alınamadı.")
        
    # AI Analizi
    analysis = ai_analyst.analyze_article(scraped_data['title'], scraped_data['content'])
    
    # --- ACTION ENGINE TRIGGER (Deep Scan) ---
    if analysis.get("impact_score", 0) >= 80:
        print(f"🚀 ACTION ENGINE: High Impact ({analysis['impact_score']}) detected in SCAN. Generating Report...")
        
        report_html = f"""
        <h1>⚡ INTELLIGENCE ALERT: {analysis.get('impact_score')} / 100</h1>
        <h2>{scraped_data['title']}</h2>
        <p><a href="{request.url}">Original Source</a></p>
        <hr>
        <h3>🤖 AI Insight</h3>
        <p>{analysis.get('aiInsight')}</p>
        <h3>📝 Summary</h3>
        <p>{analysis.get('summary')}</p>
        <hr>
        <h3>Full Content Analysis</h3>
        <p>{scraped_data['content'][:2000]}...</p>
        """
        
        # upload_res = drive_service.upload_html_as_doc(f"SCAN ALERT: {scraped_data['title']}", report_html)
        
        # if upload_res.get("status") == "success":
        #    analysis["action_taken"] = "IMMEDIATE_REPORT_GENERATED"
        #    analysis["report_link"] = upload_res.get("link")
        print("ℹ️ Auto-Upload skipped to prevent duplicates. User can Archive manually.")
        analysis["action_taken"] = "AUTO_UPLOAD_DISABLED"
    
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
            "models/gemini-1.5-flash",
            "gemini-1.5-flash",
            "models/gemini-1.5-flash-latest",
            "gemini-1.5-flash-latest",
            "models/gemini-pro",
            "gemini-pro"
        ]
        model = None
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                break
            except:
                continue
        
        if not model:
            raise HTTPException(status_code=500, detail="No working Gemini model found")
        
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
    if db_url:
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
            return psycopg2.connect(db_url)
    
    # 3. Last resort: Raise error instead of connecting to localhost
    raise Exception("Database connection failed: DB_HOST and DB_PASSWORD environment variables are required. Cannot connect to localhost in Cloud Run.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
