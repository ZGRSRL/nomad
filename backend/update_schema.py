import psycopg2
import os
from urllib.parse import urlparse
from pathlib import Path
from dotenv import load_dotenv

# Try to load .env, but ignore errors (like encoding)
try:
    env_path = Path(__file__).parent / '.env'
    # Try different encodings
    try:
        load_dotenv(dotenv_path=env_path, encoding='utf-8')
    except UnicodeDecodeError:
        print("Warning: .env is not UTF-8, trying latin-1...")
        load_dotenv(dotenv_path=env_path, encoding='latin-1')
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

def connect_db():
    """Attempt to connect using Env vars, URL, or Hardcoded Fallback"""
    
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

    # 2. DB URL
    db_url = os.getenv("DB_URL")
    if db_url:
        try:
             return psycopg2.connect(db_url, sslmode="require")
        except:
             pass

    # 3. Hardcoded Fallback (Supabase) - Derived from init_db.py
    print("Trying Hardcoded Fallback...")
    # Clean env to prevent interference
    if "DB_URL" in os.environ:
        del os.environ["DB_URL"]
        
    return psycopg2.connect(
        user="postgres",
        password="Fm5%g69!jnnVgQn",
        host="db.twfyvroqefyhhlasdkdn.supabase.co",
        port="5432",
        dbname="postgres",
        sslmode="require",
        options="-c client_encoding=UTF8"
    )

def update_schema():
    conn = None
    try:
        conn = connect_db()
        print("Connected to DB.")
        cur = conn.cursor()
        
        commands = [
            "ALTER TABLE feeds ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE feeds ADD COLUMN IF NOT EXISTS last_fetch_status TEXT;",
            "ALTER TABLE feeds ADD COLUMN IF NOT EXISTS last_fetch_time TIMESTAMP;",
            "ALTER TABLE feeds ADD COLUMN IF NOT EXISTS failure_count INTEGER DEFAULT 0;",
            "CREATE INDEX IF NOT EXISTS idx_feeds_active ON feeds(is_active);"
        ]

        for cmd in commands:
            print(f"Executing: {cmd}")
            cur.execute(cmd)
        
        conn.commit()
        print("✅ Schema updated successfully!")
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    update_schema()
