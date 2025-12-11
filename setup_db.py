import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    # Connect to default postgres DB
    print("Connecting to 'postgres' database...")
    conn = psycopg2.connect("postgresql://postgres:mypassword@localhost:5432/postgres?sslmode=disable")
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
