import feedparser
import psycopg2
import os
import asyncio
import aiohttp
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import datetime

# --- CONFIG & CONSTANTS ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/rss+xml, application/xml, application/atom+xml, text/xml'
}

# --- DB CONNECTION ---
def connect_db():
    """Robust Database Connection Strategy"""
    # 1. Direct Env Vars
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
        return None

# --- DATABASE MANAGEMENT ---

def get_db_feeds(active_only=True):
    """
    Retrieves feeds from DB. 
    Returns a list of dicts: [{'id': 1, 'url': '...', 'category': '...', 'source_name': '...'}]
    """
    feeds = []
    conn = connect_db()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        query = "SELECT id, url, categoryvb, source_name FROM feeds"
        
        # Check if is_active column exists (graceful degradation if migration didn't run)
        try:
            if active_only:
                cur.execute("SELECT id, url, categoryvb, source_name FROM feeds WHERE is_active = TRUE")
            else:
                cur.execute(query)
        except:
            conn.rollback()
            print("WARNING: 'is_active' column missing. Fetching all.")
            cur.execute(query)
            
        rows = cur.fetchall()
        for r in rows:
            feeds.append({
                "id": r[0],
                "url": r[1],
                "category": r[2],
                "source_name": r[3]
            })
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Read Error: {e}")
        if conn: conn.close()
        return []

def delete_feed_from_db(feed_id):
    """Deletes a feed by ID"""
    conn = connect_db()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM feeds WHERE id = %s", (feed_id,))
        conn.commit()
        affected = cur.rowcount
        cur.close()
        conn.close()
        return affected > 0
    except Exception as e:
        print(f"DB Delete Error: {e}")
        return False

def add_feed_to_db(url, category, source_name="UNKNOWN"):
    """Adds a new RSS feed."""
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO feeds (url, categoryvb, source_name, is_active) VALUES (%s, %s, %s, TRUE) RETURNING id",
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

def delete_feed_from_db(feed_id):
    """Permanently removes a feed."""
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM feeds WHERE id = %s", (feed_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"DB Delete Error: {e}")
        return False

def toggle_feed_status(feed_id, is_active):
    """Enables or disables a feed."""
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("UPDATE feeds SET is_active = %s WHERE id = %s", (is_active, feed_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"DB Toggle Error: {e}")
        return False

def update_feed_stats(feed_id, status, error_msg=None):
    """
    Updates the last_fetch_status and increments failure_count if needed.
    Should be called after an attempt.
    """
    try:
        conn = connect_db()
        if not conn: return
        cur = conn.cursor()
        
        now = datetime.datetime.now()
        
        if status == "SUCCESS":
            cur.execute("""
                UPDATE feeds 
                SET last_fetch_status = 'SUCCESS', last_fetch_time = %s, failure_count = 0 
                WHERE id = %s
            """, (now, feed_id))
        else:
            # FAILURE: Increment count
            cur.execute("""
                UPDATE feeds 
                SET last_fetch_status = 'ERROR', last_fetch_time = %s, failure_count = failure_count + 1 
                WHERE id = %s
            """, (now, feed_id))
            
            # Check for auto-disable (e.g., > 5 failures)
            cur.execute("SELECT failure_count FROM feeds WHERE id = %s", (feed_id,))
            fc = cur.fetchone()[0]
            if fc >= 5:
                print(f"⚠️ Feed {feed_id} disabled due to too many failures ({fc}).")
                cur.execute("UPDATE feeds SET is_active = FALSE WHERE id = %s", (feed_id,))
                
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        # Silent fail for stats update prevents cascading errors
        print(f"Stats Update Error: {e}")

# --- ASYNC FETCHING LOGIC ---

async def fetch_og_image(session, url):
    """
    Fetches the Open Graph image from a URL.
    This is an expensive fallback, use sparingly.
    """
    try:
        async with session.get(url, headers=HEADERS, timeout=5) as response:
            if response.status != 200:
                return None
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try og:image
            og_img = soup.find('meta', property='og:image')
            if og_img and og_img.get('content'):
                return og_img['content']
            
            # Try twitter:image
            tw_img = soup.find('meta', name='twitter:image')
            if tw_img and tw_img.get('content'):
                return tw_img['content']
                
    except Exception:
        return None
    return None

def clean_summary(html_content):
    """Removes HTML tags and cleans up whitespace."""
    if not html_content: return ""
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=' ')
    return text.strip()

async def process_feed(session, feed_data):
    """
    Fetches and parses a single RSS feed.
    feed_data: dict with id, url, category, source_name
    """
    url = feed_data['url']
    articles = []
    
    try:
        async with session.get(url, headers=HEADERS, timeout=10) as response:
            if response.status != 200:
                update_feed_stats(feed_data['id'], "ERROR")
                return []
            
            content = await response.read()
            feed = feedparser.parse(content)
            
            if not feed.entries:
                if feed.bozo:
                    update_feed_stats(feed_data['id'], "ERROR")
                return []
            
            # Success
            update_feed_stats(feed_data['id'], "SUCCESS")
            
            source_title = feed_data['source_name'] or feed.feed.get("title", "Unknown")[:15].upper()
            
            # Process first 5 entries (don't overwhelm)
            for entry in feed.entries[:5]: 
                # Image Extraction
                image_url = None
                
                # 1. media_content
                if 'media_content' in entry:
                    for media in entry.media_content:
                        if media.get('type', '').startswith('image/'):
                            image_url = media.get('url')
                            break
                            
                # 2. media_thumbnail
                if not image_url and 'media_thumbnail' in entry:
                    thumbnails = entry.media_thumbnail
                    if thumbnails:
                        image_url = thumbnails[0].get('url')
                        
                # 3. links
                if not image_url and 'links' in entry:
                    for link in entry.links:
                        if link.get('type', '').startswith('image/'):
                            image_url = link.get('href')
                            break
                            
                # 4. Summary Regex
                if not image_url and 'summary' in entry:
                    img_match = re.search(r'src=["\'](https?://[^"\']+\.(?:jpg|jpeg|png|gif|webp))["\']', entry.summary, re.IGNORECASE)
                    if img_match:
                        image_url = img_match.group(1)
                
                # 5. OG Fallback (Async) - Only if no image found yet
                # Note: This increases time. Maybe only do it for important feeds? 
                # For now, let's skip OG fallback in the main loop to keep it fast, 
                # or do it only if we really need it. User asked for it.
                # Let's do it but with strict timeout in fetch_og_image
                if not image_url:
                    image_url = await fetch_og_image(session, entry.link)

                # 6. Favicon Fallback (Last resort)
                if not image_url:
                    parsed_uri = urlparse(url)
                    image_url = '{uri.scheme}://{uri.netloc}/favicon.ico'.format(uri=parsed_uri)

                # Summary Sanitization
                raw_summary = entry.get("summary", "")
                clean_text = clean_summary(raw_summary)[:200] + "..."

                articles.append({
                    "id": entry.get("id", entry.link),
                    "source": source_title,
                    "category": feed_data['category'],
                    "title": entry.title,
                    "link": entry.link,
                    "image_url": image_url,
                    "time": entry.get("published", "Recent"),
                    "summary": clean_text,
                    "isLive": True
                })
                
    except Exception as e:
        # print(f"Feed Error {url}: {e}")
        update_feed_stats(feed_data['id'], "ERROR")
        
    return articles

async def fetch_feeds_async(category="ALL"):
    """
    Main entry point for fetching feeds.
    """
    all_feeds = get_db_feeds(active_only=True)
    
    # Filter by category if needed
    if category != "ALL":
        all_feeds = [f for f in all_feeds if f['category'] == category]
        
    async with aiohttp.ClientSession() as session:
        tasks = [process_feed(session, f) for f in all_feeds]
        results = await asyncio.gather(*tasks)
        
    # Flatten list
    flat_articles = [item for sublist in results for item in sublist]
    
    # Deduplicate by URL (simple)
    seen_links = set()
    unique_articles = []
    for art in flat_articles:
        if art['link'] not in seen_links:
            seen_links.add(art['link'])
            unique_articles.append(art)
            
    return unique_articles

def verify_rss_url(url):
    """Sync verification for adding new feeds via Admin UI"""
    try:
        import requests
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
             return False, f"HTTP Error: {response.status_code}"

        feed = feedparser.parse(response.content)
        
        if feed.bozo and not feed.entries: 
            return False, f"Invalid RSS XML: {feed.bozo_exception}"
        
        if not feed.entries:
            return False, "No entries found in this RSS feed."
            
        return True, "Valid"
    except Exception as e:
        return False, str(e)
