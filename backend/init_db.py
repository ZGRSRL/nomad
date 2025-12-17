import psycopg2
import os

def init_db():
    print("Connecting to Supabase...")
    try:
        # Explicit connection params to avoid URI parsing bugs
        conn = psycopg2.connect(
            user="postgres",
            password="Fm5%g69!jnnVgQn",
            host="db.twfyvroqefyhhlasdkdn.supabase.co",
            port="5432",
            dbname="postgres",
            sslmode="require"
        )
        cur = conn.cursor()
        
        # 1. FEEDS TABLE
        print("Checking 'feeds' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feeds (
                id SERIAL PRIMARY KEY,
                url TEXT UNIQUE NOT NULL,
                categoryVB TEXT,
                source_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 2. AGENT MEMORY TABLE
        print("Checking 'agent_memory' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agent_memory (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding TEXT, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Note: Embedding vector type requires pgvector, but here we use TEXT for compatibility/mock if extension missing.
        
        conn.commit()
        cur.close()
        conn.close()
        print("SUCCESS: Database schema initialized.")
        
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    init_db()
