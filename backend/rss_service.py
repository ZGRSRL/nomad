import feedparser
import psycopg2
import requests
import os

import feedparser
import psycopg2
import requests
import os
from urllib.parse import urlparse

# DB Bağlantısı - Robust Connection Helper
def connect_db():
    # 1. Direct Env Vars
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER", "postgres")
    
    if db_pass and db_host:
        return psycopg2.connect(
            database="postgres",
            user=db_user,
            password=db_pass,
            host=db_host,
            port=5432,
            sslmode="require"
        )

    # 2. Fallback to URL
    db_url = os.getenv("DB_URL", "postgresql://postgres:mypassword@localhost:5432/nomad?sslmode=disable")
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
        print(f"DB Connect Error: {e}")
        # Fallback
        return psycopg2.connect(db_url)

# Anti-Bot Headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/rss+xml, application/xml, application/atom+xml, text/xml'
}

def get_db_feeds():
    """Veritabanındaki kayıtlı RSS linklerini kategori bazlı gruplayıp getirir."""
    feeds = {}
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT url, categoryvb, source_name FROM feeds")
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
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO feeds (url, categoryvb, source_name) VALUES (%s, %s, %s) RETURNING id",
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
            # Requests ile çek (User-Agent için)
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            source_title = feed.feed.get("title", "Unknown")[:15].upper()
            
            if not feed.entries:
                raise Exception("No content in feed")

            for entry in feed.entries[:3]: 
                published = entry.get("published", "Just now")
                
                # --- IMAGE EXTRACTION LOGIC ---
                image_url = None
                
                # 1. Try media_content (Standard RSS Media)
                if 'media_content' in entry:
                    for media in entry.media_content:
                        if media.get('type', '').startswith('image/'):
                            image_url = media.get('url')
                            break
                
                # 2. Try media_thumbnail
                if not image_url and 'media_thumbnail' in entry:
                    thumbnails = entry.media_thumbnail
                    if thumbnails:
                        image_url = thumbnails[0].get('url')

                # 3. Try links (Enclosures)
                if not image_url and 'links' in entry:
                    for link in entry.links:
                        if link.get('type', '').startswith('image/'):
                            image_url = link.get('href')
                            break
                            
                # 4. Try parsing summary for <img src="..."> using regex
                if not image_url and 'summary' in entry:
                    import re
                    # Look for http(s) followed by typical image extensions, handling single or double quotes
                    # Matches src="URL" or src='URL'
                    img_match = re.search(r'src=["\'](https?://[^"\']+\.(?:jpg|jpeg|png|gif|webp))["\']', entry.summary, re.IGNORECASE)
                    if img_match:
                        image_url = img_match.group(1)

                # Fallback placeholder if needed (handled in frontend usually, but explicitly None here)
                
                articles.append({
                    "id": entry.get("id", entry.link),
                    "source": source_title,
                    "category": cat,
                    "title": entry.title,
                    "link": entry.link,
                    "image_url": image_url, # NEW FIELD
                    "time": published[:16],
                    "summary": entry.get("summary", "")[:200] + "...",
                    "isLive": True
                })
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            # Hata oluşursa kullanıcıya bildir
            articles.append({
                "id": f"error-{url}",
                "source": "SYSTEM ALERT",
                "category": "ERROR",
                "title": f"SIGNAL LOST: {url}",
                "link": "#",
                "image_url": None,
                "time": "NOW",
                "summary": f"Could not retrieve data from source. Error: {str(e)}",
                "isLive": False
            })

    return articles

def verify_rss_url(url):
    """RSS linkinin geçerli olup olmadığını kontrol eder"""
    try:
        # Requests ile çek (User-Agent için)
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
             return False, f"HTTP Error: {response.status_code}"

        feed = feedparser.parse(response.content)
        
        if feed.bozo and not feed.entries: # XML Hatası varsa ve hiç içerik yoksa
            return False, f"Invalid RSS XML: {feed.bozo_exception}"
        
        if not feed.entries:
            return False, "No entries found in this RSS feed."
            
        return True, "Valid"
    except Exception as e:
        return False, str(e)
