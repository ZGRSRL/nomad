import psycopg2
import sys

# Force stdout to UTF-8 to avoid Windows console encoding errors
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# Credentials from init_db.py
host = "db.twfyvroqefyhhlasdkdn.supabase.co"
dbname = "postgres"
user = "postgres"
password = "Fm5%g69!jnnVgQn"
port = 5432

print(f"Connecting to {host}...")

try:
    conn = psycopg2.connect(
        host=host,
        database=dbname,
        user=user,
        password=password,
        port=port,
        sslmode='require'
    )
    cursor = conn.cursor()
    
    print("Connected! Executing schema updates...")
    
    sqls = [
        "ALTER TABLE feeds ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;",
        "ALTER TABLE feeds ADD COLUMN IF NOT EXISTS last_fetch_status TEXT;",
        "ALTER TABLE feeds ADD COLUMN IF NOT EXISTS last_fetch_time TIMESTAMP;",
        "ALTER TABLE feeds ADD COLUMN IF NOT EXISTS failure_count INTEGER DEFAULT 0;",
        "CREATE INDEX IF NOT EXISTS idx_feeds_active ON feeds(is_active);"
    ]
    
    for sql in sqls:
        print(f"Executing: {sql}")
        cursor.execute(sql)
        
    conn.commit()
    print("Migration SUCCESS! Database schema is now up to date.")
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"MIGRATION FAILED with error: {e}")
