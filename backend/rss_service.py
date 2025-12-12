import feedparser
import psycopg2

# DB Bağlantısı
DB_CONN = "postgresql://postgres:mypassword@localhost:5432/nomad?sslmode=disable"

def get_db_feeds():
    """Veritabanındaki kayıtlı RSS linklerini kategori bazlı gruplayıp getirir."""
    feeds = {}
    try:
        conn = psycopg2.connect(DB_CONN)
        cur = conn.cursor()
        cur.execute("SELECT url, categoryVB, source_name FROM feeds")
        rows = cur.fetchall()
        
        for url, cat, name in rows:
            if cat not in feeds:
                feeds[cat] = []
            feeds[cat].append(url)
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Read Error: {e}")
        return {} # Hata olursa boş dön
    return feeds

def add_feed_to_db(url, category, source_name="UNKNOWN"):
    """Yeni RSS kaynağı ekler"""
    try:
        conn = psycopg2.connect(DB_CONN)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO feeds (url, categoryVB, source_name) VALUES (%s, %s, %s) RETURNING id",
            (url, category.upper(), source_name.upper())
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return new_id
    except Exception as e:
        print(f"DB Insert Error: {e}")
        return None

def fetch_feeds(category="ALL"):
    articles = []
    # Veritabanından kaynakları çek
    feed_sources = get_db_feeds()
    
    target_urls = []
    
    # Kategoriye göre filtrele
    if category == "ALL":
        for cat, urls in feed_sources.items():
            target_urls.extend([(u, cat) for u in urls])
    elif category in feed_sources:
        target_urls = [(u, category) for u in feed_sources[category]]
    
    # RSS'leri çek
    for url, cat in target_urls:
        try:
            feed = feedparser.parse(url)
            source_title = feed.feed.get("title", "Unknown")[:15].upper()
            
            for entry in feed.entries[:3]: 
                published = entry.get("published", "Just now")
                articles.append({
                    "id": entry.get("id", entry.link),
                    "source": source_title,
                    "category": cat,
                    "title": entry.title,
                    "link": entry.link,
                    "time": published[:16],
                    "summary": entry.get("summary", "")[:200] + "...",
                    "isLive": True
                })
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            
    return articles
