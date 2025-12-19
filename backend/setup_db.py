import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Veritabanı bağlantı bilgisi
DB_PARAMS = {
    "dbname": "nomad",
    "user": "postgres",
    "password": "mypassword",
    "host": "localhost",
    "port": "5432"
}

def setup_database():
    try:
        # 1. Bağlan
        conn = psycopg2.connect(**DB_PARAMS)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # 2. Feeds Tablosunu Oluştur (RSS Kaynakları için)
        print("Creating 'feeds' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feeds (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL UNIQUE,
                categoryvb TEXT NOT NULL,
                source_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. Varsayılan Kaynakları Ekle (Boş kalmasın)
        default_feeds = [
            ("https://www.wired.com/feed/category/ai/latest/rss", "AI / TECH", "WIRED"),
            ("https://techcrunch.com/category/artificial-intelligence/feed/", "AI / TECH", "TECHCRUNCH"),
            ("https://www.theverge.com/rss/index.xml", "AI / TECH", "THE VERGE"),
            ("https://feeds.feedburner.com/TheHackersNews", "CYBERSEC", "HACKERNEWS"),
            ("https://www.sciencedaily.com/rss/top/science.xml", "SCIENCE", "SCIENCEDAILY")
        ]
        
        for url, cat, name in default_feeds:
            # Çakışma varsa (ON CONFLICT) hiçbir şey yapma
            cur.execute("""
                INSERT INTO feeds (url, categoryvb, source_name) 
                VALUES (%s, %s, %s) 
                ON CONFLICT (url) DO NOTHING;
            """, (url, cat, name))

        print("✅ Veritabanı güncellendi: 'feeds' tablosu ve varsayılanlar hazır.")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    setup_database()
