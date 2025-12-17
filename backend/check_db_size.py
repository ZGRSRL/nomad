
import psycopg2

DB_PARAMS = {
    "dbname": "nomad",
    "user": "postgres",
    "password": "mypassword",
    "host": "localhost",
    "port": "5432"
}

try:
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("SELECT pg_size_pretty(pg_database_size('nomad'));")
    size = cur.fetchone()
    if size:
        print(f"Database Size: {size[0]}")
    
    # Check largest tables
    cur.execute("""
        SELECT relname as "Table",
               pg_size_pretty(pg_total_relation_size(relid)) as "Size"
        FROM pg_catalog.pg_statio_user_tables 
        ORDER BY pg_total_relation_size(relid) DESC;
    """)
    rows = cur.fetchall()
    print("\nTable Sizes:")
    for row in rows:
        print(f"{row[0]}: {row[1]}")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
