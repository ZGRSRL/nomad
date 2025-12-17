import psycopg2
import sys

# Credentials
DB_HOST = "db.twfyvroqefyhhlasdkdn.supabase.co"
DB_PASS = "Fm5%g69!jnnVgQn]"
DB_USER = "postgres"
DB_NAME = "postgres"

print(f"Testing connection to {DB_HOST} with user {DB_USER}...")

try:
    conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=5432,
        sslmode="require"
    )
    print("SUCCESS: Connection established.")
    conn.close()
except Exception as e:
    print("FAILED:")
    print(e)
