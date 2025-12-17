import os

# DB Bağlantısı
DB_URL = os.getenv("DB_URL", "postgresql://postgres:mypassword@localhost:5432/nomad?sslmode=disable")
# Cloud'da 'postgres' database'ine baglanmak yerine direkt DB_URL kullanilir
# Ancak lokalde 'nomad' veritabanini yaratmak icin once 'postgres' db'ye baglanmak gerekir
# Bu script cloud deploy oncesi lokalde calistirildigi varsayimiyla yazilmistir
# Cloud'da Supabase zaten hazir oldugu icin bu scriptin oraya baglanip extension acmasi yeterli
DEFAULT_DB_URL = os.getenv("DB_URL", "postgresql://postgres:mypassword@localhost:5432/postgres?sslmode=disable")

try:
    # Connect to default DB or provided DB (Cloud)
    print(f"Connecting to database...")
    conn = psycopg2.connect(DEFAULT_DB_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Check if DB exists
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'nomad'")
    exists = cur.fetchone()
    if not exists:
        print("Creating 'nomad' database...")
        cur.execute("CREATE DATABASE nomad;")
    else:
        print("'nomad' database already exists.")
    
    cur.close()
    conn.close()

    # Connect to nomad DB
    print("Connecting to 'nomad' database...")
    conn = psycopg2.connect("postgresql://postgres:mypassword@localhost:5432/nomad?sslmode=disable")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    print("Creating 'vector' extension...")
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    print("✅ Success: Database created and vector extension enabled.")
    
    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
